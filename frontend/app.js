const API_BASE = "http://127.0.0.1:8000";

const documentFile = document.getElementById("documentFile");
const uploadButton = document.getElementById("uploadButton");
const uploadStatus = document.getElementById("uploadStatus");
const documentsList = document.getElementById("documentsList");

const questionInput = document.getElementById("questionInput");
const askButton = document.getElementById("askButton");
const chatResult = document.getElementById("chatResult");


async function loadDocuments() {
    const response = await fetch(
        `${API_BASE}/api/documents`
    );

    if (!response.ok) {
        throw new Error("Failed to load documents.");
    }

    const documents = await response.json();

    if (documents.length === 0) {
        documentsList.innerHTML =
            "<p>No documents uploaded yet.</p>";
        return;
    }

    documentsList.innerHTML = documents.map(document => `
        <div class="document-item">
            <div>
                <strong>${escapeHtml(document.filename)}</strong>
                <br>
                <small>${document.size} bytes</small>
            </div>

            <div class="document-actions">
                <button
                    onclick="downloadDocument(${document.id})"
                >
                    Download
                </button>

                <button
                    onclick="deleteDocument(${document.id})"
                >
                    Delete
                </button>
            </div>
        </div>
    `).join("");
}


async function uploadDocument() {
    const file = documentFile.files[0];

    if (!file) {
        uploadStatus.textContent =
            "Please select a file first.";
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    uploadStatus.textContent = "Uploading...";

    try {
        const response = await fetch(
            `${API_BASE}/api/documents`,
            {
                method: "POST",
                body: formData
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Upload failed."
            );
        }

        uploadStatus.textContent =
            "Document uploaded successfully.";

        documentFile.value = "";

        await loadDocuments();

    } catch (error) {
        uploadStatus.textContent = error.message;
    }
}


async function downloadDocument(id) {
    window.open(
        `${API_BASE}/api/documents/${id}/download`,
        "_blank"
    );
}


async function deleteDocument(id) {
    const response = await fetch(
        `${API_BASE}/api/documents/${id}`,
        {
            method: "DELETE"
        }
    );

    if (!response.ok) {
        alert("Failed to delete document.");
        return;
    }

    await loadDocuments();
}


async function askQuestion() {
    const question = questionInput.value.trim();

    if (!question) {
        chatResult.innerHTML =
            "<p>Please enter a question.</p>";
        return;
    }

    chatResult.innerHTML =
        "<p>Thinking...</p>";

    try {
        const response = await fetch(
            `${API_BASE}/api/chat`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    question: question
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Chat request failed."
            );
        }

        renderChatResult(data);

    } catch (error) {
        chatResult.innerHTML =
            `<p>${escapeHtml(error.message)}</p>`;
    }
}


function renderChatResult(data) {
    const sources = data.sources || [];

    chatResult.innerHTML = `
        <h3>Answer</h3>

        <div class="answer">
            ${escapeHtml(data.answer)}
        </div>

        <h3>Sources</h3>

        ${
            sources.length
                ? sources.map(source => `
                    <div class="source">
                        <strong>
                            ${escapeHtml(source.filename)}
                        </strong>

                        <br>

                        <small>
                            Relevance score: ${source.score}
                        </small>

                        <p>
                            ${escapeHtml(source.snippet)}
                        </p>
                    </div>
                `).join("")
                : "<p>No matching sources found.</p>"
        }
    `;
}


function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = value;
    return div.innerHTML;
}


uploadButton.addEventListener(
    "click",
    uploadDocument
);

askButton.addEventListener(
    "click",
    askQuestion
);


loadDocuments().catch(error => {
    documentsList.innerHTML =
        `<p>${escapeHtml(error.message)}</p>`;
});