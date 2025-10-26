/**
 * Main App Component
 * Manages the receipt splitting workflow
 */
import { useState } from "react";
import { ReceiptUpload, PeopleInput } from "./components/UploadFlow";
import { ReceiptDisplay } from "./components/ReceiptDisplay";
import { ChatInterface } from "./components/ChatInterface";
import { AssignmentSummary } from "./components/AssignmentSummary";
import { useConversation } from "./hooks/useConversation";
import { useAssignmentState } from "./hooks/useAssignmentState";
import {
  uploadReceipt,
  getReceiptResult,
  startConversation,
  confirmSplit,
} from "./utils/api";
import "./App.css";

function App() {
  // Workflow state
  const [step, setStep] = useState("upload"); // upload, people, processing, chat
  const [receiptFile, setReceiptFile] = useState(null);
  const [processingToken, setProcessingToken] = useState(null);
  const [parsedReceipt, setParsedReceipt] = useState(null);
  const [people, setPeople] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [error, setError] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  // Hooks for conversation and assignment state
  const conversation = useConversation(conversationId);
  const assignmentState = useAssignmentState(conversationId);

  // Handle receipt upload
  const handleReceiptUpload = async (file) => {
    console.log("📤 Uploading receipt:", file.name, file.size, "bytes");
    setReceiptFile(file);
    setError(null);
    setIsProcessing(true);

    try {
      const response = await uploadReceipt(file);
      console.log("✅ Upload response:", response);
      console.log("🎫 Token received:", response.token);

      setProcessingToken(response.token);
      setStep("processing");

      // Poll for results
      pollReceiptResult(response.token);
    } catch (err) {
      console.error("❌ Upload failed:", err);
      setError("Failed to upload receipt: " + err.message);
      setIsProcessing(false);
    }
  };

  // Poll for receipt processing results
  const pollReceiptResult = async (token) => {
    console.log("🔄 Will start polling in 2 seconds for token:", token);

    const poll = async () => {
      console.log(`📊 Polling attempt for token:`, token);

      try {
        const result = await getReceiptResult(token);
        console.log(`📥 Poll response:`, result);

        if (result.status === "done" && result.result) {
          console.log("✅ Receipt processing completed!", result.result);
          setParsedReceipt(result.result);
          setStep("people");
          setIsProcessing(false);
        } else if (result.status === "failed") {
          console.error("❌ Receipt processing failed:", result);
          setError(
            "Receipt processing failed: " + (result.message || "Unknown error")
          );
          setStep("upload");
          setIsProcessing(false);
        } else if (result.status === "pending") {
          console.log(
            `⏳ Status: ${result.message}. Polling again in 2 seconds...`
          );
          setTimeout(poll, 2000); // Poll every 2 seconds
        }
      } catch (err) {
        console.error(`❌ Poll error:`, err);
        setError("Failed to get receipt result: " + err.message);
        setStep("upload");
        setIsProcessing(false);
      }
    };

    // Wait 2 seconds before starting to poll
    setTimeout(poll, 2000);
  };

  // Handle people input and start conversation
  const handlePeopleSubmit = async (peopleList) => {
    setPeople(peopleList);
    setError(null);
    setIsProcessing(true);

    try {
      const response = await startConversation(parsedReceipt, peopleList);
      setConversationId(response.conversation_id);

      // Add welcome message to conversation
      conversation.setMessages([
        {
          role: "assistant",
          content: response.message,
          timestamp: new Date().toISOString(),
        },
      ]);

      setStep("chat");
      setIsProcessing(false);
    } catch (err) {
      setError("Failed to start conversation: " + err.message);
      setIsProcessing(false);
    }
  };

  // Handle sending messages
  const handleSendMessage = async (message) => {
    try {
      const response = await conversation.send(message);

      // Update highlighted items
      if (response.highlighted_items) {
        assignmentState.setHighlightedItems(response.highlighted_items);
      }

      // Refresh assignment state
      await assignmentState.refresh();
    } catch (err) {
      setError("Failed to send message: " + err.message);
    }
  };

  // Handle confirm split
  const handleConfirmSplit = async () => {
    setError(null);

    try {
      const result = await confirmSplit(conversationId);
      alert(
        `Split confirmed! Total: $${Object.values(result.totals)
          .reduce((a, b) => a + b, 0)
          .toFixed(2)}`
      );
    } catch (err) {
      setError("Failed to confirm split: " + err.message);
    }
  };

  // Reset to start over
  const handleReset = () => {
    setStep("upload");
    setReceiptFile(null);
    setProcessingToken(null);
    setParsedReceipt(null);
    setPeople([]);
    setConversationId(null);
    setError(null);
    setIsProcessing(false);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🧾 Receipt Splitter</h1>
        <p>Split bills with AI - Just chat naturally!</p>
      </header>

      {error && (
        <div className="error-banner">
          <span>{error}</span>
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      <main className="app-main">
        {step === "upload" && (
          <div className="step-container">
            <ReceiptUpload
              onUploadSuccess={handleReceiptUpload}
              onError={setError}
            />
          </div>
        )}

        {step === "processing" && (
          <div className="step-container">
            <div className="processing-indicator">
              <div className="spinner"></div>
              <h3>Processing your receipt...</h3>
              <p>This may take a moment</p>
            </div>
          </div>
        )}

        {step === "people" && (
          <div className="step-container">
            <PeopleInput
              onPeopleChange={setPeople}
              onSubmit={handlePeopleSubmit}
            />
          </div>
        )}

        {step === "chat" && conversationId && (
          <div className="chat-layout">
            <div className="chat-sidebar">
              <ReceiptDisplay
                receipt={parsedReceipt}
                assignments={assignmentState.assignmentState?.item_assignments}
                highlightedItems={assignmentState.highlightedItems}
              />
              <AssignmentSummary
                totals={assignmentState.totals}
                people={people}
                unassignedCount={assignmentState.unassignedItems?.length || 0}
                onConfirm={handleConfirmSplit}
              />
            </div>

            <div className="chat-main">
              <ChatInterface
                messages={conversation.messages}
                onSendMessage={handleSendMessage}
                isLoading={conversation.isLoading}
              />
            </div>
          </div>
        )}
      </main>

      {step !== "upload" && (
        <button className="reset-button" onClick={handleReset}>
          Start Over
        </button>
      )}
    </div>
  );
}

export default App;
