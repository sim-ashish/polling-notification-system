const API_BASE_URL = "http://localhost:8000";


const userIdInput =
    document.getElementById("userId");

const badge =
    document.getElementById("notificationBadge");

const bell =
    document.getElementById("notificationBell");

const status =
    document.getElementById("status");

const sendNotificationButton =
    document.getElementById("sendNotification");


let previousCount = 0;


async function fetchUnreadCount() {

    const userId = userIdInput.value;

    try {

        const response = await fetch(
            `${API_BASE_URL}/notifications/unread-count?user_id=${userId}`
        );

        if (!response.ok) {
            throw new Error(
                "Failed to fetch unread count"
            );
        }

        const data = await response.json();

        updateNotificationBadge(
            data.unread_count
        );

    } catch (error) {

        console.error(error);

        status.textContent =
            "Unable to fetch notifications.";
    }
}


function updateNotificationBadge(count) {

    badge.textContent = count;

    if (count > 0) {
        badge.style.display = "flex";
    } else {
        badge.style.display = "none";
    }

    if (count > previousCount) {
        shakeBell();
    }

    previousCount = count;

    status.textContent =
        `Unread notifications: ${count}`;
}


function shakeBell() {

    bell.classList.remove("shake");

    void bell.offsetWidth;

    bell.classList.add("shake");
}


sendNotificationButton.addEventListener(
    "click",
    async () => {

        const userId =
            Number(userIdInput.value);

        try {

            const response = await fetch(
                `${API_BASE_URL}/notifications`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        user_id: userId,

                        notification_type:
                            "connection_request",

                        title:
                            "New Connection Request",

                        message:
                            "Someone sent you a connection request"
                    })
                }
            );

            if (!response.ok) {
                throw new Error(
                    "Failed to create notification"
                );
            }

            status.textContent =
                "Notification created.";

        } catch (error) {

            console.error(error);

            status.textContent =
                "Failed to create notification.";
        }
    }
);


// Initial request
fetchUnreadCount();


// Poll every 5 seconds
setInterval(
    fetchUnreadCount,
    5000
);