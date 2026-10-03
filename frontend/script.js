const API_BASE_URL =
    "http://localhost:8000";


const userIdInput =
    document.getElementById(
        "userId"
    );

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

let eventSource = null;


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
// Update badge
// ----------------------------------------------

function updateNotificationBadge(
    count
) {

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
// Handle SSE notification
// ----------------------------------------------

function handleNotification(
    event
) {

    const notification =
        JSON.parse(
            event.data
        );


    console.log(
        "New notification:",
        notification
    );


    status.textContent =
        notification.message;


    fetchUnreadCount();


    shakeBell();
}


// ----------------------------------------------
// Connect to SSE
// ----------------------------------------------

function connectToNotificationStream() {

    const userId =
        userIdInput.value;


    if (eventSource) {

        eventSource.close();
    }


    eventSource =
        new EventSource(
            `${API_BASE_URL}/notifications/stream?user_id=${userId}`
        );


    eventSource.addEventListener(
        "notification",
        handleNotification
    );


    eventSource.onopen = () => {

        status.textContent =
            "Connected to notification stream.";
    };


    eventSource.onerror = () => {

        status.textContent =
            "Notification stream disconnected. Browser will retry...";
    };
}


// ----------------------------------------------
// Create test notification
// ----------------------------------------------

sendNotificationButton.addEventListener(
    "click",
    async () => {

        const userId =
            Number(
                userIdInput.value
            );


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
// Start SSE
// ----------------------------------------------

connectToNotificationStream();