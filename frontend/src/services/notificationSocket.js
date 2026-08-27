let socket = null;

export function connectNotificationSocket(userId, onMessage) {
    if (!userId) {
        return;
    }

    socket = new WebSocket(
        `ws://127.0.0.1:8000/ws/notifications/${userId}`
    );

    socket.onopen = () => {
        console.log("Notification WebSocket connected");
    };

    socket.onmessage = (event) => {
        try {
            const notification = JSON.parse(event.data);

            console.log(
                "New notification:",
                notification
            );

            onMessage(notification);

        } catch (error) {
            console.error(
                "Invalid WebSocket message:",
                error
            );
        }
    };

    socket.onerror = (error) => {
        console.error(
            "WebSocket error:",
            error
        );
    };

    socket.onclose = () => {
        console.log(
            "Notification WebSocket disconnected"
        );
    };

    return socket;
}


export function disconnectNotificationSocket() {
    if (socket) {
        socket.close();
        socket = null;
    }
}