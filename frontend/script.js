const API_BASE_URL =
    "http://localhost:8000";


const userIdInput =
    document.getElementById("userId");

const badge =
    document.getElementById(
        "notificationBadge"
    );

const bell =
    document.getElementById(
        "notificationBell"
    );

const status =
    document.getElementById(
        "status"
    );

const sendNotificationButton =
    document.getElementById(
        "sendNotification"
    );


let previousCount = 0;

let lastNotificationId = 0;

let longPollingActive = true;


// ----------------------------------------------
// Fetch unread count
// ----------------------------------------------

async function fetchUnreadCount() {

    const userId =
        userIdInput.value;

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/notifications/unread-count` +
                `?user_id=${userId}`
            );

        if (!response.ok) {

            throw new Error(
                "Failed to fetch unread count"
            );
        }

        const data =
            await response.json();

        updateNotificationBadge(
            data.unread_count
        );

    } catch (error) {

        console.error(error);

        status.textContent =
            "Unable to fetch notification count.";
    }
}


// ----------------------------------------------
// Update bell
// ----------------------------------------------

function updateNotificationBadge(count) {

    badge.textContent =
        count;

    if (count > 0) {

        badge.style.display =
            "flex";

    } else {

        badge.style.display =
            "none";
    }

    if (count > previousCount) {

        shakeBell();
    }

    previousCount =
        count;
}


// ----------------------------------------------
// Bell animation
// ----------------------------------------------

function shakeBell() {

    bell.classList.remove(
        "shake"
    );

    void bell.offsetWidth;

    bell.classList.add(
        "shake"
    );
}


// ----------------------------------------------
// Long Polling
// ----------------------------------------------

async function longPollNotifications() {

    if (!longPollingActive) {
        return;
    }

    const userId =
        userIdInput.value;

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/notifications/long-poll` +
                `?user_id=${userId}` +
                `&last_notification_id=${lastNotificationId}`
            );

        if (!response.ok) {

            throw new Error(
                "Long polling request failed"
            );
        }

        const data =
            await response.json();


        if (
            data.notification_available &&
            data.notification
        ) {

            const notification =
                data.notification;


            lastNotificationId =
                notification.id;


            status.textContent =
                notification.message;


            await fetchUnreadCount();


            shakeBell();
        }


    } catch (error) {

        console.error(error);

        status.textContent =
            "Long polling connection failed.";
    }


    // Immediately start another request
    longPollNotifications();
}


// ----------------------------------------------
// Create test notification
// ----------------------------------------------

sendNotificationButton.addEventListener(
    "click",
    async () => {

        const userId =
            Number(userIdInput.value);

        try {

            const response =
                await fetch(
                    `${API_BASE_URL}/notifications`,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({

                            user_id:
                                userId,

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


// ----------------------------------------------
// Initial state
// ----------------------------------------------

fetchUnreadCount();


// ----------------------------------------------
// Start long polling
// ----------------------------------------------

longPollNotifications();