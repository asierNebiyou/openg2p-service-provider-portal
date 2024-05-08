import json
import logging
from datetime import datetime

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class G2pServiceProviderBenificiaryManagement(http.Controller):
    @http.route("/serviceprovider/group", type="http", auth="public", website=True)
    def group_list(self, **kw):
        group = (
            request.env["res.partner"]
            .sudo()
            .search(
                [
                    ("active", "=", True),
                    ("is_registrant", "=", True),
                    ("is_group", "=", True),
                ]
            )
        )

        return request.render("g2p_service_provider_benificiary_management.group_list", {"groups": group})

    @http.route(
        ["/serviceprovider/group/create/"],
        type="http",
        auth="user",
        website=True,
        csrf=False,
    )
    def group_create(self, **kw):
        gender = request.env["gender.type"].sudo().search([])
        return request.render(
            "g2p_service_provider_benificiary_management.group_create_form_template", {"gender": gender}
        )

    @http.route(
        ["/serviceprovider/group/create/submit"],
        type="http",
        auth="user",
        website=True,
        csrf=False,
    )
    def group_create_submit(self, **kw):
        try:
            beneficiary_id = int(kw.get("group_id"))

            beneficiary = request.env["res.partner"].sudo().browse(beneficiary_id)
            if not beneficiary:
                return request.render(
                    "g2p_service_provider_benificiary_management.error_template",
                    {"error_message": "Beneficiary not found."},
                )

            for key, value in kw.items():
                if key in beneficiary:
                    beneficiary.write({key: value})
                else:
                    print(f"Ignoring invalid key: {key}")

            return request.redirect("/serviceprovider/group")

        except Exception as e:
            _logger.info("Error occurred%s" % e)
            return request.render(
                "g2p_service_provider_benificiary_management.error_template",
                {"error_message": "An error occurred. Please try again later."},
            )

    @http.route(
        ["/serviceprovider/group/update/<int:_id>"],
        type="http",
        auth="user",
        website=True,
        csrf=False,
    )
    def group_update(self, _id, **kw):
        try:
            gender = request.env["gender.type"].sudo().search([])
            beneficiary = request.env["res.partner"].sudo().browse(_id)
            if not beneficiary:
                return request.render(
                    "g2p_service_provider_benificiary_management.error_template",
                    {"error_message": "Beneficiary not found."},
                )

            return request.render(
                "g2p_service_provider_benificiary_management.group_update_form_template",
                {"beneficiary": beneficiary, "gender": gender},
            )
        except Exception:
            return request.render(
                "g2p_service_provider_benificiary_management.error_template",
                {"error_message": "Invalid URL."},
            )

    @http.route(
        ["/serviceprovider/group/submit/"],
        type="http",
        auth="user",
        website=True,
        csrf=False,
    )
    def group_submit(self, **kw):
        try:
            beneficiary_id = int(kw.get("id"))

            beneficiary = request.env["res.partner"].sudo().browse(beneficiary_id)
            if not beneficiary:
                return request.render(
                    "g2p_service_provider_benificiary_management.error_template",
                    {"error_message": "Beneficiary not found."},
                )

            for key, value in kw.items():
                if key in beneficiary:
                    beneficiary.write({key: value})
                else:
                    print(f"Ignoring invalid key: {key}")

            return request.redirect("/serviceprovider/group")
            # return request.render("g2p_service_provider_benificiary_management.g2p_success_template")

        except Exception as e:
            _logger.info("Error occurred%s" % e)
            return request.render(
                "g2p_service_provider_benificiary_management.error_template",
                {"error_message": "An error occurred. Please try again later."},
            )

    @http.route("/serviceprovider/individual/<int:_id>", type="http", auth="public", website=True)
    def individual_list(self, _id, **kw):
        try:
            gender = request.env["gender.type"].sudo().search([])
            group = (
                request.env["res.partner"]
                .sudo()
                .search(
                    [
                        ("active", "=", True),
                        ("is_registrant", "=", True),
                        ("is_group", "=", True),
                        ("id", "=", _id),
                    ]
                )
            )

            return request.render(
                "g2p_service_provider_benificiary_management.individual_list",
                {
                    "individuals": group.group_membership_ids.mapped("individual"),
                    "group": group,
                    "gender": gender,
                },
            )
        except Exception as e:
            _logger.info("Error:%s" % e)
            return request.render(
                "g2p_service_provider_benificiary_management.error_template",
                {"error_message": "Invalid URL."},
            )

    @http.route(
        ["/serviceprovider/individual/create/submit"],
        type="http",
        auth="user",
        website=True,
        csrf=False,
    )
    def individual_create_submit(self, **kw):
        try:
            given_name = kw.get("given_name")
            family_name = kw.get("family_name")
            addl_name = kw.get("addl_name")

            name = f"{given_name}, {addl_name} {family_name}"

            partner_data = {
                "name": name,
                "given_name": given_name,
                "family_name": family_name,
                "addl_name": addl_name,
                "is_registrant": True,
                "is_group": False,
            }

            # TODO: Relationshio logic need to build later
            if kw.get("relationship"):
                kw.pop("relationship")

            partner_data.update(kw)

            ind = request.env["res.partner"].sudo().create(partner_data)

            group_id = kw.get("id")
            if group_id:
                group_id = request.env["res.partner"].sudo().browse(int(group_id))

                request.env["g2p.group.membership"].sudo().create(
                    {
                        "group": group_id.id,
                        "individual": ind.id,
                        "kind": [],
                    }
                )

            return request.redirect(f"/serviceprovider/individual/{group_id.id}")

        except Exception as e:
            _logger.error("Error occurred: %s" % e)
            return request.render(
                "g2p_service_provider_benificiary_management.error_template",
                {"error_message": "An error occurred. Please try again later."},
            )

    @http.route(
        ["/serviceprovider/individual/update/"],
        type="http",
        auth="user",
        website=True,
        csrf=False,
    )
    def individual_update(self, **kw):
        try:
            gender = request.env["gender.type"].sudo().search([])
            beneficiary = request.env["res.partner"].sudo().browse(int(kw.get("mem")))
            if not beneficiary:
                return request.render(
                    "g2p_service_provider_benificiary_management.error_template",
                    {"error_message": "Beneficiary not found."},
                )

            return request.render(
                "g2p_service_provider_benificiary_management.individual_update_form_template",
                {"beneficiary": beneficiary, "gender": gender, "group": int(kw.get("group"))},
            )
        except Exception:
            return request.render(
                "g2p_service_provider_benificiary_management.error_template",
                {"error_message": "Invalid URL."},
            )

    @http.route(
        ["/serviceprovider/individual/update/submit/"],
        type="http",
        auth="user",
        website=True,
        csrf=False,
    )
    def individual_submit(self, **kw):
        try:
            group_id = kw.get("group")
            beneficiary = request.env["res.partner"].sudo().browse(int(kw.get("id")))
            if not beneficiary:
                return request.render(
                    "g2p_service_provider_benificiary_management.error_template",
                    {"error_message": "Beneficiary not found."},
                )
            for key, value in kw.items():
                if key in beneficiary:
                    beneficiary.write({key: value})
                else:
                    print(f"Ignoring invalid key: {key}")

            return request.redirect(f"/serviceprovider/individual/{group_id}")
            # return request.render("g2p_service_provider_benificiary_management.g2p_success_template")

        except Exception as e:
            _logger.error("Error occurred: %s" % e)
            return request.render(
                "g2p_service_provider_benificiary_management.error_template",
                {"error_message": "An error occurred. Please try again later."},
            )

    # Creating members
    @http.route(
        ["/serviceprovider/individual/create/"],
        type="http",
        auth="user",
        website=True,
        csrf=False,
    )
    def individual_create(self, **kw):
        res = dict()
        try:
            # Group creation
            if kw.get("group_id"):
                group_rec = request.env["res.partner"].sudo().browse(int(kw.get("group_id")))
            else:
                name = kw.get("household_name")
                if name:
                    group_rec = (
                        request.env["res.partner"]
                        .sudo()
                        .create({"name": name, "is_registrant": True, "is_group": True})
                    )

            given_name = kw.get("given_name")
            family_name = kw.get("family_name")
            addl_name = kw.get("addl_name")

            name = f"{given_name}, {addl_name} {family_name}"

            partner_data = {
                "name": name,
                "given_name": given_name,
                "family_name": family_name,
                "addl_name": addl_name,
                "birthdate": kw.get("birthdate"),
                "gender": kw.get("gender"),
                "is_registrant": True,
                "is_group": False,
            }

            # TODO: Relationship logic need to build later
            if kw.get("relationship"):
                kw.pop("relationship")

            individual = request.env["res.partner"].sudo().create(partner_data)

            print("individual##################WWWW", individual)

            # Add the individual to the group membership
            membership = (
                request.env["g2p.group.membership"]
                .sudo()
                .create(
                    {
                        "group": group_rec.id,
                        "individual": individual.id,
                        "kind": [],
                    }
                )
            )

            print("membership##################WWWW", membership)

            member_list = []

            for membership in group_rec.group_membership_ids:
                member_list.append(
                    {
                        "id": membership.individual.id,
                        "name": membership.individual.name,
                        "age": membership.individual.age,
                        "gender": membership.individual.gender,
                        "active": membership.individual.active,
                        "group_id": membership.group.id,
                    }
                )

            print("MEMME####LIST", member_list)
            res["member_list"] = member_list
            return json.dumps(res)

        except Exception as e:
            _logger.info("ERROR LOG IN INDIVIDUAL%s", e)

    @http.route(
        "/serviceprovider/member/update/",
        type="http",
        auth="user",
        website=True,
        csrf=False,
    )
    def update_member(self, **kw):
        # Get member ID from request data
        member_id = kw.get("member_id")
        try:
            member = request.env["res.partner"].sudo().browse(int(member_id))
            print("BIRTHDATE###########", member.birthdate, member)
            if member:
                exist_value = {
                    "given_name": member.given_name,
                    "addl_name": member.addl_name,
                    "family_name": member.family_name,
                    "dob": str(member.birthdate),
                    "gender": member.gender,
                }
                return json.dumps(exist_value)

        except Exception as e:
            _logger.info("ERROR LOG IN UPDATE MEMBER%s", e)

    @http.route(
        "/serviceprovider/member/update/submit/",
        type="http",
        auth="user",
        website=True,
        csrf=False,
    )
    def update_member_submit(self, **kw):
        try:
            member = request.env["res.partner"].sudo().browse(int(kw.get("member_id")))
            print("MEB-old####################kw", member.given_name, kw)
            res = dict()
            if member:
                # Update the member record
                birthdate = datetime.strptime(kw["birthdate"], "%Y-%m-%d").date()
                print("birthdate-----", birthdate)
                member.write(
                    {
                        "given_name": kw["given_name"],
                        "addl_name": kw["addl_name"],
                        "family_name": kw["family_name"],
                        "birthdate": birthdate if birthdate else None,
                        "gender": kw["gender"],
                    }
                )
                print("MEB-after####################kw", member.given_name, kw)

                group = request.env["res.partner"].sudo().browse(int(kw.get("group_id")))
                print("group####################kw", group)

                member_list = []
                for membership in group.group_membership_ids:
                    member_list.append(
                        {
                            "id": membership.individual.id,
                            "name": membership.individual.name,
                            "age": membership.individual.age,
                            "gender": membership.individual.gender,
                            "active": membership.individual.active,
                            "group_id": membership.group.id,
                        }
                    )
                res["member_list"] = member_list
                print("RES#########################", res)

                return json.dumps(res)

        except Exception as e:
            _logger.info("Error occurred during member submit: %s", e)
            return json.dumps({"error": "Failed to update member details"})

    # Showing members
    # @http.route(
    #     ["/serviceprovider/group/membership/list/<int:group_id>"],
    #     type="http",
    #     auth="user",
    #     website=True,
    #     csrf=False,
    # )
    # def group_membership_list(self, group_id, **kw):
    #     try:
    #         # Fetch the group
    #         group = request.env["res.partner"].sudo().browse(group_id)
    #         member_list = []
    #         if group.group_membership_ids:
    #             # Iterate through group memberships and collect member information
    #             for membership in group.group_membership_ids:
    #                 member_list.append({
    #                     'id': membership.individual.id,
    #                     'name': membership.individual.name,
    #                     'age': membership.individual.age,
    #                     'gender': membership.individual.gender,
    #                     'relationship': membership.individual.relationship,
    #                     'active': membership.individual.active,
    #                     'group_id': membership.group.id,
    #                 })

    #             # Return the list of memberships as JSON
    #             return json.dumps(member_list)

    #     except Exception as e:
    #         _logger.error("Error fetching group membership list: %s", e)
    #         return json.dumps({"error": str(e)})
