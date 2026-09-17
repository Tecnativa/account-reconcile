# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tools.sql import column_exists


def migrate(env, version):
    if column_exists(env.cr, "account_reconcile_model", "type"):
        env.cr.execute(
            """
            SELECT DISTINCT ON (company_id)
                id,
                company_id,
                past_months_limit,
                auto_reconcile,
                unique_matching,
                match_partner,
                match_same_currency,
                match_text_location_label,
                match_text_location_note,
                match_text_location_reference
            FROM account_reconcile_model
            WHERE type = 'invoice_matching'
            ORDER BY company_id, id
            """
        )
        for (
            account_reconcile_model_id,
            company_id,
            past_months_limit,
            auto_reconcile,
            unique_matching,
            match_partner,
            match_same_currency,
            match_text_location_label,
            match_text_location_note,
            match_text_location_reference,
        ) in env.cr.fetchall():
            company = env["res.company"].browse(company_id)
            company.write(
                {
                    "auto_reconcile_invoices_past_months_limit": past_months_limit,
                    "auto_reconcile_invoices_auto_reconcile": auto_reconcile,
                    "auto_reconcile_invoices_unique_matching": unique_matching,
                    "auto_reconcile_invoices_match_partner": match_partner,
                    "auto_reconcile_invoices_match_same_currency": match_same_currency,
                    "auto_reconcile_invoices_match_text_location_label": match_text_location_label,  # noqa E501,
                    "auto_reconcile_invoices_match_text_location_note": match_text_location_note,  # noqa E501,
                    "auto_reconcile_invoices_match_text_location_reference": match_text_location_reference,  # noqa E501,
                }
            )
            # auto_reconcile_invoices_match_partner_ids field
            env.cr.execute(
                """
                INSERT INTO res_company_res_partner_rel (
                    res_company_id,
                    res_partner_id
                )
                SELECT company_id, res_partner_id
                FROM account_reconcile_model_res_partner_rel
                WEHERE account_reconcile_model_id = %s
                """[account_reconcile_model_id],
            )
            # auto_reconcile_invoices_match_partner_category_ids field
            env.cr.execute(
                """
                INSERT INTO res_company_res_partner_category_rel (
                    res_company_id,
                    res_partner_category_id
                )
                SELECT company_id, res_partner_category_id
                FROM account_reconcile_model_res_partner_category_rel
                WEHERE account_reconcile_model_id = %s
                """,
                [account_reconcile_model_id],
            )
