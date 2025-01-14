function App() {
    const [ticketId, setTicketId] = React.useState('');
    const [qrCode, setQrCode] = React.useState(null);
    const [error, setError] = React.useState(null);
    const [loading, setLoading] = React.useState(false);
    const [ticketData, setTicketData] = React.useState(null);

    async function generateQR() {
        const ticketId = document.getElementById('ticketId').value;
        if (!ticketId) {
            alert('Please enter a ticket ID');
            return;
        }

        try {
            setLoading(true);
            setError(null);
            
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ ticketId }),
            });

            const data = await response.json();
            if (data.error) {
                throw new Error(data.error);
            }
            
            setQrCode(data.qrData);
            setTicketData(data.ticketData);
            
        } catch (err) {
            setError(err.message);
            setQrCode(null);
            setTicketData(null);
        } finally {
            setLoading(false);
        }
    };

    function printQR() {
        const qrImage = document.querySelector('.qr-image');
        if (!qrImage) return;

        const printWindow = window.open('', '', 'width=600,height=600');
        printWindow.document.write('<html><head><title>Print QR Code</title>');
        printWindow.document.write('<style>body { margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }</style>');
        printWindow.document.write('</head><body>');
        printWindow.document.write('<img src="' + qrImage.src + '" style="width: 100mm; height: 100mm;">');
        printWindow.document.write('</body></html>');
        printWindow.document.close();
        printWindow.focus();
        printWindow.print();
        printWindow.close();
    };

    function copyQR() {
        const qrImage = document.querySelector('.qr-image');
        if (!qrImage) return;

        const canvas = document.createElement('canvas');
        canvas.width = qrImage.width;
        canvas.height = qrImage.height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(qrImage, 0, 0);
        
        canvas.toBlob(function(blob) {
            const item = new ClipboardItem({ "image/png": blob });
            navigator.clipboard.write([item]).then(
                () => alert('QR code copied to clipboard!'),
                () => alert('Failed to copy QR code')
            );
        });
    };

    return (
        <div className="container">
            <h1 className="text-center mb-4">Lottery Ticket Generator</h1>
            
            <div className="mb-3">
                <label htmlFor="ticketId" className="form-label">Ticket ID:</label>
                <div className="input-group">
                    <input
                        type="text"
                        className="form-control"
                        id="ticketId"
                        value={ticketId}
                        onChange={(e) => setTicketId(e.target.value)}
                        placeholder="Enter ticket ID"
                    />
                    <button
                        className="btn btn-primary"
                        onClick={generateQR}
                        disabled={loading || !ticketId}
                    >
                        {loading ? 'Generating...' : 'Generate QR'}
                    </button>
                </div>
            </div>

            {error && (
                <div className="alert alert-danger" role="alert">
                    {error}
                </div>
            )}

            {qrCode && (
                <div className="text-center">
                    <div className="qr-container print-container">
                        <img
                            src={`data:image/png;base64,${qrCode}`}
                            alt="QR Code"
                            className="qr-image"
                        />
                    </div>
                    
                    <div className="btn-group">
                        <button className="btn btn-success me-2" onClick={printQR}>
                            Print QR
                        </button>
                        <button className="btn btn-info" onClick={copyQR}>
                            Copy QR
                        </button>
                    </div>

                    {ticketData && (
                        <div className="mt-4">
                            <h3>Ticket Information</h3>
                            <pre className="bg-light p-3 rounded">
                                {JSON.stringify(ticketData, null, 2)}
                            </pre>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

ReactDOM.render(<App />, document.getElementById('root'));
