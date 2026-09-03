
let socket = null;
let currentUserId = null;
let manuallyClosed = false;

export function connectNotificationSocket(userId, onMessage) {
  if (!userId) {
    console.warn(
      "Notification WebSocket: userId is missing"
    );

    return null;
  }

  // --------------------------------------------------
  // Prevent duplicate connection for same user
  // --------------------------------------------------

  if (
    socket &&
    currentUserId === userId &&
    (
      socket.readyState === WebSocket.OPEN ||
      socket.readyState === WebSocket.CONNECTING
    )
  ) {
    console.log(
      "Notification WebSocket already exists"
    );

    return socket;
  }

  // --------------------------------------------------
  // Close previous socket if it belongs to another
  // user
  // --------------------------------------------------

  if (socket) {
    try {
      manuallyClosed = true;
      socket.close();
    } catch (error) {
      console.error(
        "Error closing previous WebSocket:",
        error
      );
    }

    socket = null;
  }

  currentUserId = userId;
  manuallyClosed = false;

  const wsUrl =
    `ws://127.0.0.1:8000/ws/notifications/${userId}`;

  console.log(
    "Connecting to Notification WebSocket:",
    wsUrl
  );

  const newSocket = new WebSocket(wsUrl);

  socket = newSocket;

  // --------------------------------------------------
  // Connection opened
  // --------------------------------------------------

  newSocket.onopen = () => {
    console.log(
      "Notification WebSocket connected"
    );
  };

  // --------------------------------------------------
  // Receive notification
  // --------------------------------------------------

  newSocket.onmessage = (event) => {
    try {
      const notification =
        JSON.parse(event.data);

      console.log(
        "New notification:",
        notification
      );

      if (onMessage) {
        onMessage(notification);
      }

    } catch (error) {
      console.error(
        "Invalid WebSocket message:",
        error
      );
    }
  };

  // --------------------------------------------------
  // WebSocket error
  // --------------------------------------------------

  newSocket.onerror = (error) => {
    console.error(
      "Notification WebSocket error:",
      error
    );
  };

  // --------------------------------------------------
  // WebSocket closed
  // --------------------------------------------------

  newSocket.onclose = (event) => {
    console.log(
      "Notification WebSocket disconnected",
      {
        code: event.code,
        reason: event.reason,
        wasClean: event.wasClean
      }
    );

    // Only clear the global socket if this is
    // still the active socket.
    if (socket === newSocket) {
      socket = null;

      if (!manuallyClosed) {
        currentUserId = null;
      }
    }
  };

  return newSocket;
}


// --------------------------------------------------
// Disconnect
// --------------------------------------------------

export function disconnectNotificationSocket() {
  if (!socket) {
    return;
  }

  console.log(
    "Closing Notification WebSocket"
  );

  manuallyClosed = true;

  try {
    socket.close();
  } catch (error) {
    console.error(
      "Error closing Notification WebSocket:",
      error
    );
  }

  socket = null;
  currentUserId = null;
}


// --------------------------------------------------
// Connection status
// --------------------------------------------------

export function isNotificationSocketConnected() {
  return (
    socket !== null &&
    socket.readyState === WebSocket.OPEN
  );
}
