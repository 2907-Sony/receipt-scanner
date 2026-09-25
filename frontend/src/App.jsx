import { useState, useRef } from "react";
import receiptImage from "./assets/Payment_Bill.png";
import { Camera, Store, DollarSign } from "lucide-react";
import "./App.css";

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [currentView, setCurrentView] = useState("upload");
  const [searchTerm, setSearchTerm] = useState("");
  const [receipts, setReceipts] = useState([]);
  const [selectedReceipt, setSelectedReceipt] = useState(null);
  const cameraInputRef = useRef(null);

  const handleScan = async () => {
    if (!selectedFile) {
      alert("Please select the file first");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await fetch("http://127.0.0.1:8000/upload", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      console.log(data);
    } catch (error) {
      console.error("Upload failed:", error);
    }
  };

  const fetchReceipts = async () => {
    try {
      const url = searchTerm
        ? `http://127.0.0.1:8000/receipts/search?store_name=${searchTerm}`
        : `http://127.0.0.1:8000/receipts`;
      const response = await fetch(url);
      const data = await response.json();
      setReceipts(data);
    } catch (error) {
      console.error("Failed to fetch receipts:", error);
    }
  };

  const fetchReceiptDetail = async (id) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/receipts/${id}`);
      const data = await response.json();
      setSelectedReceipt(data);
      setCurrentView("detail");
    } catch (error) {
      console.error("Failed to fetch receipt detail:", error);
    }
  };

  return (
    <div className="app-wrapper">
      <div
        className="scanner-card"
        style={{
          background: "#8236FF",
          padding: "2rem 1.5rem",
          position: "relative",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            position: "absolute",
            top: "-40px",
            right: "-40px",
            width: "140px",
            height: "150px",
            background: "#FFFF66",
            borderRadius: "50%",
            opacity: 0.3,
          }}
        ></div>

        <div style={{ position: "relative" }}>
          <div
            style={{
              background: "transparent",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "10px",
              marginBottom: "1.5rem",
            }}
          >
            <img
              src={receiptImage}
              alt="Receipt illustration"
              style={{ width: "35px", background: "transparent" }}
            />
            <p
              style={{
                fontSize: "30px",
                fontWeight: 600,
                margin: 0,
                color: "white",
              }}
            >
              Receipt scanner
            </p>
          </div>

          {currentView === "upload" && (
            <>
              <div
                style={{
                  background: "rgba(255,255,255,0.1)",
                  border: "1.5px dashed #FFFF66",
                  borderRadius: "20px",
                  padding: "3rem 1.25rem",
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  gap: "15px",
                }}
              >
                <p
                  style={{
                    fontSize: "22px",
                    color: "white",
                    margin: 0,
                    textAlign: "center",
                  }}
                >
                  {selectedFile ? selectedFile.name : "Choose a receipt photo"}
                </p>
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => setSelectedFile(e.target.files[0])}
                />
                <button
                  onClick={() => cameraInputRef.current.click()}
                  className="camera-button"
                >
                  <Camera size={18} />
                </button>
              </div>

              <input
                type="file"
                accept="image/*"
                capture="environment"
                ref={cameraInputRef}
                style={{ display: "none" }}
                onChange={(e) => {
                  setSelectedFile(e.target.files[0]);
                }}
              />

              <button
                onClick={handleScan}
                style={{
                  width: "100%",
                  marginTop: "1.25rem",
                  fontSize: "16px",
                  background: "#FFFF66",
                  color: "#4a4a00",
                  border: "none",
                  padding: "12px",
                  borderRadius: "10px",
                  fontWeight: 500,
                }}
              >
                Scan receipt
              </button>
              <button
                onClick={() => {
                  setCurrentView("history");
                  fetchReceipts();
                }}
                style={{
                  width: "100%",
                  marginTop: "10px",
                  fontSize: "16px",
                  background: "transparent",
                  color: "white",
                  border: "1.5px solid rgba(255,255,255,0.5)",
                  padding: "12px",
                  borderRadius: "10px",
                  fontWeight: 500,
                }}
              >
                View receipts
              </button>
            </>
          )}

          {currentView === "history" && (
            <div>
              <div
                style={{ display: "flex", gap: "8px", marginBottom: "1.5rem" }}
              >
                <input
                  type="text"
                  placeholder="Search by store name..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  style={{
                    flex: 1,
                    padding: "10px 14px",
                    borderRadius: "10px",
                    border: "none",
                    fontSize: "15px",
                  }}
                />
                <button
                  onClick={fetchReceipts}
                  style={{
                    background: "#FFFF66",
                    color: "#4a4a00",
                    border: "none",
                    padding: "10px 18px",
                    borderRadius: "10px",
                    fontWeight: 500,
                  }}
                >
                  Search
                </button>
              </div>

              <div>
                {receipts.map((receipt) => (
                  <div
                    key={receipt.id}
                    onClick={() => fetchReceiptDetail(receipt.id)}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      color: "white",
                      background: "rgba(255,255,255,0.08)",
                      borderRadius: "10px",
                      padding: "10px 14px",
                      marginBottom: "8px",
                      cursor: "pointer",
                    }}
                  >
                    <Store size={16} color="#FFFF66" />
                    <p style={{ margin: 0, padding: 5, color: "#FFFF66" }}>
                      {receipt.store_name}
                    </p>
                    <span
                      style={{
                        marginLeft: "auto",
                        display: "flex",
                        alignItems: "center",
                        gap: "2px",
                      }}
                    >
                      <DollarSign size={16} />
                      {receipt.total_amount}
                    </span>
                  </div>
                ))}
              </div>

              <button
                onClick={() => setCurrentView("upload")}
                style={{
                  width: "100%",
                  marginTop: "10px",
                  fontSize: "16px",
                  background: "transparent",
                  color: "white",
                  border: "1.5px solid rgba(255,255,255,0.5)",
                  padding: "12px",
                  borderRadius: "10px",
                  fontWeight: 500,
                }}
              >
                Back
              </button>
            </div>
          )}

          {currentView === "detail" && selectedReceipt && (
            <div>
              <p
                style={{
                  color: "white",
                  fontSize: "22px",
                  fontWeight: 600,
                  margin: "0 0 4px",
                }}
              >
                {selectedReceipt.store_name}
              </p>
              <p
                style={{
                  color: "rgba(255,255,255,0.7)",
                  fontSize: "14px",
                  margin: "0 0 20px",
                }}
              >
                {selectedReceipt.purchase_date}
              </p>

              <div>
                {selectedReceipt.items.map((item) => (
                  <div
                    key={item.id}
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      color: "white",
                      padding: "8px 0",
                      borderBottom: "1px solid rgba(255,255,255,0.15)",
                    }}
                  >
                    <span>{item.item_name}</span>
                    <span>${item.item_price}</span>
                  </div>
                ))}
              </div>

              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  color: "#FFFF66",
                  fontWeight: 600,
                  fontSize: "18px",
                  marginTop: "12px",
                  paddingTop: "12px",
                  borderTop: "2px solid #FFFF66",
                }}
              >
                <span>Total</span>
                <span>${selectedReceipt.total_amount}</span>
              </div>

              <button
                onClick={() => setCurrentView("history")}
                style={{
                  width: "100%",
                  marginTop: "20px",
                  fontSize: "16px",
                  background: "transparent",
                  color: "white",
                  border: "1.5px solid rgba(255,255,255,0.5)",
                  padding: "12px",
                  borderRadius: "10px",
                  fontWeight: 500,
                }}
              >
                Back
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
