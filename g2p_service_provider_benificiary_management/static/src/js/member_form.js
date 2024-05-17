// Date restriction
$(document).ready(function () {
    $(".date-picker").each(function () {
        var input = this;
        var today = new Date().toISOString().split("T")[0];
        input.setAttribute("max", today);
    });
});

function validateForm(isCreateForm) {
    var requiredFields = document.querySelectorAll(".s_website_form_field [required]");
    var isValid = true;

    requiredFields.forEach(function (field) {
        if (!field.value.trim() && field.offsetWidth > 0 && field.offsetHeight > 0) {
            // If the field is empty, display an error message next to the field
            var errorMessage = document.createElement("span");
            errorMessage.className = "error-message";
            errorMessage.textContent = "This field is required";
            errorMessage.style.color = "red";

            // Check if an error message already exists for the field
            var existingErrorMessage = field.parentNode.querySelector(".error-message");
            if (existingErrorMessage) {
                // If an error message already exists, replace it
                field.parentNode.replaceChild(errorMessage, existingErrorMessage);
            } else {
                // Otherwise, insert the error message after the field
                field.parentNode.insertBefore(errorMessage, field.nextSibling);
            }

            // Add red border to indicate the missing field
            field.style.border = "1px solid red";
            isValid = false;
        } else {
            // If the field is filled, remove any previous error message and styling
            var existingErrorMessage = field.parentNode.querySelector(".error-message");
            if (existingErrorMessage) {
                existingErrorMessage.parentNode.removeChild(existingErrorMessage);
            }
            field.style.border = "";
        }
    });

    if (isValid && isCreateForm) {
        // If all required fields are filled and it's a create form, submit the form
        document.getElementById("creategroupForm").submit();
    } else if (isValid && !isCreateForm) {
        // If all required fields are filled and it's not a create form, submit the form
        document.getElementById("updategroupForm").submit();
    }
}

function showToast(message) {
    const toast_message = $("#memberDetailModal #toast-message");
    toast_message.text(message);
    const toast_container = $("#memberDetailModal #toast-container");
    toast_container.css("display", "block");
}

function hideToast() {
    const toast_container = $("#memberDetailModal #toast-container");
    toast_container.css("display", "none");
}

function resetFormFields() {
    $("#memberDetailModal input, #memberDetailModal select").val("");
}

// Replace button
$('[data-bs-target="#memberDetailModal"]').on("click", function () {
    $("#update-member-btn").replaceWith(
        '<div id="member_submit" type="button" class="btn btn-primary create-new">Add</div>'
    );
    resetFormFields();
});

// Add button
$(document).on("click", "#member_submit", function () {
    var group = $("input[name='group_id']").val();
    // Head
    var Householdname = $("#name").val();
    var Householddob = $("#birthdate").val();
    var Householgender = $("select[name='gender']").val();
    // #member
    var firstName = $("#memberDetailModal #given_name").val();
    var middleName = $("#memberDetailModal #addl_name").val();
    var lastName = $("#memberDetailModal #family_name").val();
    var dob = $("#memberDetailModal #birthdate").val();
    console.log("DOB###########", dob, Householddob);
    var gender = $('#memberDetailModal select[name="gender"]').val();
    var relationship = $('#memberDetailModal select[name="relationship"]').val();
    var isValid = true;
    var modal = $("#memberDetailModal");

    $(".form-control, .form-select").removeClass("is-invalid");

    if (!firstName || !lastName || !gender || !dob) {
        console.log("empty");
        isValid = false;
        // Highlight empty required fields with a red border color
        $("#memberDetailModal .form-control[required], #memberDetailModal .form-select[required]").each(
            function () {
                if (!$(this).val()) {
                    $(this).addClass("is-invalid");
                }
            }
        );
    }

    if (!isValid) {
        showToast("Please fill out all required fields.");
        return;
    }

    $.ajax({
        url: "/serviceprovider/individual/create/",
        method: "POST",
        data: {
            group_id: group,
            household_name: Householdname,
            Household_dob: Householddob,
            Househol_gender: Householgender,
            given_name: firstName,
            family_name: middleName,
            addl_name: lastName,
            dob: dob,
            gender: gender,
            relationship: relationship,
        },
        dataType: "json",
        success: function (response) {
            console.log("Ajax request successful");
            console.log("Response:", response);
            if (response.member_list) {
                var member_list = response.member_list;
                if (member_list) {
                    resetFormFields();
                    modal.modal("hide");
                    console.log("member_list[0].group_id :", member_list[0].group_id);
                    $("input[name='group_id']").val(member_list[0].group_id);
                    // Hide no_list
                    $(".no_list").css("display", "none");

                    // Get the table body
                    var tableBody = $("#memberlist tbody");
                    // Clear existing rows
                    tableBody.empty();
                    $(".old-list").css("display", "none");

                    // Iterate over the member list and append rows to the table
                    member_list.forEach(function (member, index) {
                        $(".mem-list").css("display", "block");
                        var serialNumber = index + 1;
                        var newRowHtml =
                            "<tr>" +
                            "<td>" +
                            serialNumber +
                            "</td>" +
                            '<td style="color:#704880; font: normal normal 600 13px/16px Inter;">' +
                            member.name +
                            "</td>" +
                            "<td>" +
                            member.age +
                            "</td>" +
                            "<td>" +
                            member.gender +
                            "</td>" +
                            "<td>" +
                            "dependent" +
                            "</td>" +
                            "<td>" +
                            '<div class="active-button">' +
                            (member.active ? "Active" : "Inactive") +
                            "</div>" +
                            "</td>" +
                            "<td>" +
                            '<button class="btn btn-icon rounded-0" id="mem-update" store="' +
                            member.id +
                            '" title="Edit">' +
                            '<i class="fa fa-pencil"></i>' +
                            "</button>" +
                            "</td>" +
                            "</tr>";

                        tableBody.append(newRowHtml);
                    });
                }
            } else {
                console.error("Failed to create individual");
            }
        },
        error: function (error) {
            console.error("request failed");
            console.error("Error:", error);
        },
    });
});

// Edit Icon
$(document).on("click", "#mem-update", function () {
    var memberId = $(this).attr("store");
    var modal = $("#memberDetailModal");
    $.ajax({
        url: "/serviceprovider/member/update/",
        method: "POST",
        data: {
            member_id: memberId,
        },
        dataType: "json",
        success: function (response) {
            // Populate modal fields with member details
            modal.find("#given_name").val(response.given_name);
            modal.find("#addl_name").val(response.addl_name);
            modal.find("#family_name").val(response.family_name);
            modal.find("#birthdate").val(response.dob);
            modal.find('select[name="gender"]').val(response.gender);

            // Replace button
            $("#member_submit").replaceWith(
                '<div id="update-member-btn" store="' +
                    memberId +
                    '" class="btn btn-primary create-new">Update</div>'
            );

            // Show the modal
            modal.modal("show");
        },
        error: function (error) {
            console.error("Ajax request failed");
            console.error("Error:", error);
        },
    });
});

// Update member details when the update button is clicked
$(document).on("click", "#update-member-btn", function () {
    // Get the member ID
    var memberId = $(this).attr("store");

    // Get updated member details from the modal fields
    var group = $("input[name='group_id']").val();
    var firstName = $("#memberDetailModal #given_name").val();
    var middleName = $("#memberDetailModal #addl_name").val();
    var lastName = $("#memberDetailModal #family_name").val();
    var dob = $("#memberDetailModal #birthdate").val();
    var gender = $('#memberDetailModal select[name="gender"]').val();
    var isValid = true;

    $(".form-control, .form-select").removeClass("is-invalid");

    if (!firstName || !lastName || !gender) {
        isValid = false;
        // Highlight empty required fields with a red border color
        $("#memberDetailModal .form-control, #memberDetailModal .form-select").each(function () {
            if (!$(this).val().trim()) {
                $(this).addClass("is-invalid");
            }
        });
    }

    if (!isValid) {
        showToast("Please fill out all required fields.");
        return;
    }

    $.ajax({
        url: "/serviceprovider/member/update/submit/",
        method: "POST",
        data: {
            group_id: group,
            member_id: memberId,
            given_name: firstName,
            addl_name: middleName,
            family_name: lastName,
            birthdate: dob,
            gender: gender,
        },
        dataType: "json",
        success: function (response) {
            // Check if member_list exists in the response
            if (response && response.member_list) {
                var member_list = response.member_list;
                $("#memberDetailModal").modal("hide");

                // Get the table body
                var tableBody = $("#memberlist tbody");
                tableBody.empty();

                member_list.forEach(function (member, index) {
                    var serialNumber = index + 1;
                    var newRowHtml =
                        "<tr>" +
                        "<td>" +
                        serialNumber +
                        "</td>" +
                        '<td style="color:#704880; font: normal normal 600 13px/16px Inter;">' +
                        member.name +
                        "</td>" +
                        "<td>" +
                        member.age +
                        "</td>" +
                        "<td>" +
                        member.gender +
                        "</td>" +
                        "<td>" +
                        "dependent" +
                        "</td>" +
                        "<td>" +
                        '<div class="active-button">' +
                        (member.active ? "Active" : "Inactive") +
                        "</div>" +
                        "</td>" +
                        "<td>" +
                        '<button class="btn btn-icon rounded-0" id="mem-update" store="' +
                        member.id +
                        '" title="Edit">' +
                        '<i class="fa fa-pencil"></i>' +
                        "</button>" +
                        "</td>" +
                        "</tr>";
                    console.log("newRowHtml########", newRowHtml);
                    tableBody.append(newRowHtml);
                });
            } else {
                console.error("FINAL Member list not found in the response.");
            }
        },

        error: function (error) {
            console.error("Error:", error);
        },
    });
});
