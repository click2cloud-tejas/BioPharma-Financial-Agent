
// // ----------------------
// // Chat Functionality
// // ----------------------
// document.getElementById("send-btn").onclick = sendMessage;

// function sendMessage() {
//     const input = document.getElementById("user-input");
//     const text = input.value.trim();
//     if (!text) return;

//     appendMessage("user", text);
//     input.value = "";

//     fetch("/ask", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ query: text })
//     })
//     .then(res => res.json())
//     .then(data => {
//         console.log("LLM DEBUG:", data);
//         appendMessage("bot", data.answer);
//     });
// }

// function appendMessage(sender, message) {
//     const chatBox = document.getElementById("chat-box");

//     const wrapper = document.createElement("div");
//     wrapper.className = sender === "user" ? "chat-row user-row" : "chat-row bot-row";

//     const bubble = document.createElement("div");
//     bubble.className = sender === "user" ? "chat-bubble user-bubble" : "chat-bubble bot-bubble";
//     bubble.innerHTML = message;

//     wrapper.appendChild(bubble);
//     chatBox.appendChild(wrapper);

//     chatBox.scrollTop = chatBox.scrollHeight;
// }


// // ----------------------
// // Revenue Performance Logic
// // ----------------------
// document.getElementById("fetch-performance-btn").onclick = fetchPerformance;

// function fetchPerformance() {
//     const month = document.getElementById("month-select").value;

//     fetch("/api/revenue-performance", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ month: month })
//     })
//     .then(res => res.json())
//     .then(data => {


        
//         console.log("PERFORMANCE DEBUG:", data);

//         const outputDiv = document.getElementById("performance-output");
//         outputDiv.innerHTML = ""; // clear

//         if (data.status !== "success") {
//             outputDiv.innerHTML = `<span style="color:red;">${data.message}</span>`;
//             return;
//         }

//         let html = `<h4>Results for ${month}</h4>`;

//         data.results.forEach(item => {
//             html += `
//                 <div class="result-row">
//                     <b>${item.company}</b> → 
//                     <span style="color:${item.performance === 'overperforming' ? 'green' : 'red'};">
//                         ${item.performance.toUpperCase()}
//                     </span>
//                 </div>
//             `;
//         });

//         outputDiv.innerHTML = html;
//     });
// }


// ========================================
// 🚀 CHAT MESSAGE HANDLING
// ========================================

document.getElementById("send-btn").onclick = sendMessage;

function sendMessage() {
    const input = document.getElementById("user-input");
    const text = input.value.trim();
    if (!text) return;

    appendMessage("user", text);
    input.value = "";

    fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: text })
    })
        .then((res) => res.json())
        .then((data) => {
            console.log("LLM DEBUG:", data);

            // Show chatbot answer
            appendMessage("bot", data.answer);

            // =====================================
            // 📊 SHOW GENERATED CHART (VERY IMPORTANT)
            // =====================================
            if (data.chart_url) {
                const graphImage = document.getElementById("revenue-graph-img");

                // Avoid showing old cached image
                graphImage.src = data.chart_url + "?t=" + new Date().getTime();

                console.log("Graph updated:", graphImage.src);
            }
        })
        .catch((err) => console.error("Error in sendMessage:", err));
}

// ----------------------------------------
// Chat bubble appending logic
// ----------------------------------------
function appendMessage(sender, message) {
    const chatBox = document.getElementById("chat-box");

    const wrapper = document.createElement("div");
    wrapper.className =
        sender === "user" ? "chat-row user-row" : "chat-row bot-row";

    const bubble = document.createElement("div");
    bubble.className =
        sender === "user" ? "chat-bubble user-bubble" : "chat-bubble bot-bubble";
    bubble.innerHTML = message;

    wrapper.appendChild(bubble);
    chatBox.appendChild(wrapper);

    chatBox.scrollTop = chatBox.scrollHeight;
}

// ========================================
// 📈 REVENUE PERFORMANCE FETCH LOGIC
// ========================================

document.getElementById("fetch-performance-btn").onclick = fetchPerformance;

function fetchPerformance() {
    const month = document.getElementById("month-select").value;

    fetch("/api/revenue-performance", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ month: month })
    })
        .then((res) => res.json())
        .then((data) => {
            console.log("PERFORMANCE DEBUG:", data);

            const outputDiv = document.getElementById("performance-output");
            outputDiv.innerHTML = ""; // Clear previous content

            if (data.status !== "success") {
                outputDiv.innerHTML = `<span style="color:red;">${data.message}</span>`;
                return;
            }

            let html = `<h4>Results for ${month}</h4>`;

            data.results.forEach((item) => {
                html += `
                <div class="result-row">
                    <b>${item.company}</b> →
                    <span style="color:${
                        item.performance === "overperforming" ? "green" : "red"
                    };">
                        ${item.performance.toUpperCase()}
                    </span>
                </div>
            `;
            });

            outputDiv.innerHTML = html;
        })
        .catch((err) => console.error("Performance Fetch Error:", err));
}
