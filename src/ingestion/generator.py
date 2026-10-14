from __future__ import annotations

import random
from datetime import date, timedelta

from src.core.constants import (
    CH_SUPPLIERS,
    DE_SUPPLIERS,
    DE_VAT_RATES,
    CH_VAT_RATES,
    EXPECTED_VAT_BY_CATEGORY,
)
from src.core.models import (
    Country,
    Currency,
    GoodsReceipt,
    Invoice,
    PurchaseOrder,
    Supplier,
)


def _iban(country: Country, rng: random.Random) -> str:
    if country == Country.DE:
        digits = "".join(str(rng.randint(0, 9)) for _ in range(18))
        return f"DE{rng.randint(10, 99)}{digits}"
    digits = "".join(str(rng.randint(0, 9)) for _ in range(17))
    return f"CH{rng.randint(10, 99)}{digits}"


def _vat_id(country: Country, rng: random.Random) -> str:
    digits = "".join(str(rng.randint(0, 9)) for _ in range(9))
    return f"{country.value}{digits}"


def _round2(x: float) -> float:
    return round(x + 1e-9, 2)


def build_suppliers(rng: random.Random) -> list[Supplier]:
    suppliers: list[Supplier] = []
    sid = 1
    for name, category in DE_SUPPLIERS:
        suppliers.append(
            Supplier(
                supplier_id=f"SUP{sid:04d}",
                name=name,
                country=Country.DE,
                currency=Currency.EUR,
                vat_id=_vat_id(Country.DE, rng),
                iban=_iban(Country.DE, rng),
                default_gl_account=f"4{rng.randint(10000, 99999)}",
                category=category,
            )
        )
        sid += 1
    for name, category in CH_SUPPLIERS:
        suppliers.append(
            Supplier(
                supplier_id=f"SUP{sid:04d}",
                name=name,
                country=Country.CH,
                currency=Currency.CHF,
                vat_id=_vat_id(Country.CH, rng),
                iban=_iban(Country.CH, rng),
                default_gl_account=f"4{rng.randint(10000, 99999)}",
                category=category,
            )
        )
        sid += 1
    return suppliers


def build_purchase_orders(
    suppliers: list[Supplier], rng: random.Random, n: int
) -> list[PurchaseOrder]:
    pos: list[PurchaseOrder] = []
    for i in range(1, n + 1):
        s = rng.choice(suppliers)
        net = _round2(rng.uniform(200, 25_000))
        from src.core.constants import EXPECTED_VAT_BY_CATEGORY
        vat = EXPECTED_VAT_BY_CATEGORY[(s.country.value, s.category)]
        pos.append(
            PurchaseOrder(
                po_number=f"PO{i:06d}",
                supplier_id=s.supplier_id,
                currency=s.currency,
                net_amount=net,
                vat_rate=vat,
                issued_on=date(2024, 1, 1) + timedelta(days=rng.randint(0, 300)),
                requires_grn=(s.category == "goods"),
            )
        )
    return pos


def build_goods_receipts(
    pos: list[PurchaseOrder], rng: random.Random, coverage: float = 0.85
) -> list[GoodsReceipt]:
    grns: list[GoodsReceipt] = []
    gid = 1
    for po in pos:
        if not po.requires_grn:
            continue
        if rng.random() > coverage:
            continue  # deliberately missing GRN
        grns.append(
            GoodsReceipt(
                grn_number=f"GRN{gid:06d}",
                po_number=po.po_number,
                received_on=po.issued_on + timedelta(days=rng.randint(2, 30)),
                net_amount=po.net_amount,
            )
        )
        gid += 1
    return grns


def build_invoices(
    suppliers: list[Supplier],
    pos: list[PurchaseOrder],
    grns: list[GoodsReceipt],
    rng: random.Random,
    n: int,
) -> list[Invoice]:
    pos_by_supplier: dict[str, list[PurchaseOrder]] = {}
    for po in pos:
        pos_by_supplier.setdefault(po.supplier_id, []).append(po)
    # Shuffle pools so consumption order is random
    for pool in pos_by_supplier.values():
        rng.shuffle(pool)

    invoices: list[Invoice] = []
    for i in range(1, n + 1):
        s = rng.choice(suppliers)
        available_pos = pos_by_supplier.get(s.supplier_id, [])

        # 80% have a PO (if any are still unconsumed), 20% don't
        po: PurchaseOrder | None = None
        if available_pos and rng.random() < 0.8:
            po = available_pos.pop()          # consume it — never reused

        if po is not None:
            # 90% match the PO net exactly, 10% drift (price mismatch)
            if rng.random() < 0.9:
                net = po.net_amount
            else:
                drift = rng.uniform(-0.15, 0.15)
                net = _round2(po.net_amount * (1 + drift))
            vat_rate = po.vat_rate
        else:
            net = _round2(rng.uniform(150, 20_000))
            if s.country == Country.DE:
                vat_rate = rng.choice(DE_VAT_RATES)
            else:
                vat_rate = rng.choice(CH_VAT_RATES)

        # 5% tax ambiguity: wrong rate for category/country
        if rng.random() < 0.05:
            expected = EXPECTED_VAT_BY_CATEGORY[(s.country.value, s.category)]
            alternatives = (
                [r for r in DE_VAT_RATES if r != expected]
                if s.country == Country.DE
                else [r for r in CH_VAT_RATES if r != expected]
            )
            if alternatives:
                vat_rate = rng.choice(alternatives)

        vat_amount = _round2(net * vat_rate)
        gross = _round2(net + vat_amount)

        # 3% IBAN change (bank-detail fraud vector)
        if rng.random() < 0.03:
            iban = _iban(s.country, rng)
        else:
            iban = s.iban

        inv_date = date(2024, 6, 1) + timedelta(days=rng.randint(0, 180))
        due = inv_date + timedelta(days=rng.choice([14, 30, 45, 60]))

        grn_number = None
        if po is not None:
            matching = [g for g in grns if g.po_number == po.po_number]
            if matching:
                grn_number = matching[0].grn_number

        invoices.append(
            Invoice(
                invoice_id=f"INV{i:06d}",
                supplier_id=s.supplier_id,
                supplier_name=s.name,
                invoice_number=f"{s.supplier_id}-{rng.randint(100000, 999999)}",
                invoice_date=inv_date,
                due_date=due,
                currency=s.currency,
                net_amount=net,
                vat_rate=vat_rate,
                vat_amount=vat_amount,
                gross_amount=gross,
                po_number=po.po_number if po else None,
                grn_number=grn_number,
                iban=iban,
                description=f"Rechnung {s.name}",
                gl_account=s.default_gl_account,
            )
        )

    # Inject explicit duplicates: 3% of invoices get a near-copy 5-20 days later
    dupes: list[Invoice] = []
    for inv in invoices:
        if rng.random() < 0.03:
            dup = inv.model_copy(
                update={
                    "invoice_id": f"INV{len(invoices) + len(dupes) + 1:06d}",
                    "invoice_date": inv.invoice_date + timedelta(days=rng.randint(5, 20)),
                }
            )
            dup.due_date = dup.invoice_date + timedelta(days=30)
            dupes.append(dup)

    return invoices + dupes


def generate_dataset(n_invoices: int = 250, seed: int = 42) -> dict:
    rng = random.Random(seed)
    suppliers = build_suppliers(rng)
    pos = build_purchase_orders(suppliers, rng, n=300)
    grns = build_goods_receipts(pos, rng, coverage=0.85)
    invoices = build_invoices(suppliers, pos, grns, rng, n=n_invoices)
    return {
        "suppliers": suppliers,
        "purchase_orders": pos,
        "goods_receipts": grns,
        "invoices": invoices,
    }


def main() -> None:
    ds = generate_dataset()
    print(f"Suppliers:        {len(ds['suppliers'])}")
    print(f"Purchase orders:  {len(ds['purchase_orders'])}")
    print(f"Goods receipts:   {len(ds['goods_receipts'])}")
    print(f"Invoices:         {len(ds['invoices'])}")
    print()
    for inv in ds["invoices"][:5]:
        print(
            f"  {inv.invoice_id}  {inv.supplier_name:<40}  "
            f"{inv.gross_amount:>10.2f} {inv.currency.value}  "
            f"PO={inv.po_number or '-':<10} GRN={inv.grn_number or '-':<12}"
        )


if __name__ == "__main__":
    main()
