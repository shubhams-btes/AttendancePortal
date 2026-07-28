/* ==========================================
   AI Lab Attendance System
   Global JavaScript
========================================== */

document.addEventListener("DOMContentLoaded", function () {

    // =====================================
    // Auto Hide Alerts
    // =====================================

    const alerts = document.querySelectorAll(".alert");

    alerts.forEach(function (alert) {

        setTimeout(function () {

            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();

        }, 4000);

    });


    // =====================================
    // Sidebar Active Link
    // =====================================

    const currentPath = window.location.pathname;

    document.querySelectorAll(".sidebar .list-group-item").forEach(function (link) {

        if (link.getAttribute("href") === currentPath) {

            link.classList.add("active");

        }

    });


    // =====================================
    // Sidebar Toggle (Mobile)
    // =====================================

    const menuToggle = document.getElementById("menu-toggle");
    const sidebar = document.getElementById("sidebar");

    if (menuToggle && sidebar) {

        menuToggle.addEventListener("click", function () {

            sidebar.classList.toggle("d-none");

        });

    }


    // =====================================
    // Confirm Delete
    // =====================================

    document.querySelectorAll(".delete-btn").forEach(function (button) {

        button.addEventListener("click", function (e) {

            const confirmed = confirm(
                "Are you sure you want to delete this record?"
            );

            if (!confirmed) {

                e.preventDefault();

            }

        });

    });

});