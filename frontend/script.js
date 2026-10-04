const API_BASE_URL =
    "http://localhost:8000";


const WS_BASE_URL =
    "ws://localhost:8000";


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

let socket = null;


// ==============================================
// Fetch unread count
// ==============================================

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

        console.error(
            error
        );

        status.textContent =
            "Unable to fetch notification count.";
    }
}


// ==============================================
// Update notification badge
// ==============================================

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


    if (
        count >
        previousCount
    ) {

        shakeBell();
    }


    previousCount =
        count;
}


// ==============================================
// Shake bell
// ==============================================

function shakeBell() {

    bell.classList.remove(
        "shake"
    );


    void bell.offsetWidth;


    bell.classList.add(
        "shake"
    );
}


// ==============================================
// Handle WebSocket messages
// ==============================================

function handleWebSocketMessage(
    data
) {

    console.log(
        "Received WebSocket message:",
        data
    );


    if (
        data.type ===
        "notification"
    ) {

        const notification =
            data.data;


        status.textContent =
            notification.message;


        fetchUnreadCount();


        shakeBell();
    }
}


// ==============================================
// Connect WebSocket
// ==============================================

function connectWebSocket() {

    const userId =
        userIdInput.value;


    if (socket) {

        socket.close();
    }


    socket =
        new WebSocket(
            `${WS_BASE_URL}/ws/notifications/${userId}`
        );


    socket.onopen = () => {

        console.log(
            "WebSocket connected."
        );


        status.textContent =
            "WebSocket connected.";
    };


    socket.onmessage = (
        event
    ) => {

        const data =
            JSON.parse(
                event.data
            );


        handleWebSocketMessage(
            data
        );
    };


    socket.onerror = (
        error
    ) => {

        console.error(
            "WebSocket error:",
            error
        );


        status.textContent =
            "WebSocket error.";
    };


    socket.onclose = () => {

        console.log(
            "WebSocket disconnected."
        );


        status.textContent =
            "WebSocket disconnected.";
    };
}


// ==============================================
// Create notification
// ==============================================

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

            console.error(
                error
            );


            status.textContent =
                "Failed to create notification.";
        }
    }
);


// ==============================================
// Initial application startup
// ==============================================

fetchUnreadCount();

connectWebSocket();