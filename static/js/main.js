document.addEventListener("DOMContentLoaded", () => {
    // Handle Signup
    const signupForm = document.getElementById("signupForm");
    if (signupForm) {
        signupForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const username = document.getElementById("username").value;
            const password = document.getElementById("password").value;

            const response = await fetch("/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password }),
            });

            const data = await response.json();
            if (response.ok) {
                alert(data.message);
                window.location.href = "/login";
            } else {
                alert(data.error);
            }
        });
    }

    // Handle Login
    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const username = document.getElementById("username").value;
            const password = document.getElementById("password").value;

            const response = await fetch("/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password }),
            });

            const data = await response.json();
            if (response.ok) {
                localStorage.setItem("accessToken", data.access_token);
                window.location.href = "/chats";
            } else {
                alert(data.error);
            }
        });
    }

    // Handle Chats
    const newChatBtn = document.getElementById("newChatBtn");
    if (newChatBtn) {
        newChatBtn.addEventListener("click", () => {
            document.getElementById("newChatForm").style.display = "block";
        });

        const newChatForm = document.getElementById("newChatForm");
        newChatForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const chatTopic = document.getElementById("chatTopic").value;
            const token = localStorage.getItem("accessToken");

            const response = await fetch("/create_chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({ chatTopic }),
            });

            const data = await response.json();
            if (response.ok) {
                alert(data.message);
                location.reload();
            } else {
                alert(data.error);
            }
        });
    }
});
