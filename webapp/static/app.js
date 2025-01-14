function App() {
    const [ticketId, setTicketId] = React.useState('');
    const [qrCode, setQrCode] = React.useState(null);
    const [error, setError] = React.useState(null);
    const [loading, setLoading] = React.useState(false);
    const [ticketData, setTicketData] = React.useState(null);

    const generateQR = async () => {
        try {
            setLoading(true);
            setError(null);
            
            const response = await fetch('http://localhost:5000/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    ticket_id: ticketId,
                }),
            });
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            setQrCode(data.qr_code);
            setTicketData(data.ticket_data);
            
        } catch (err) {
            setError(err.message);
            setQrCode(null);
            setTicketData(null);
        } finally {
            setLoading(false);
        }
    };

    const printQR = () => {
        window.print();
    };

    const copyQR = async () => {
        try {
            const img = document.querySelector('.qr-image');
            const canvas = document.createElement('canvas');
            canvas.width = img.width;
            canvas.height = img.height;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0);
            
            canvas.toBlob(async (blob) => {
                const item = new ClipboardItem({ 'image/png': blob });
                await navigator.clipboard.write([item]);
                alert('QR code copied to clipboard!');
            });
        } catch (err) {
            alert('Failed to copy QR code: ' + err.message);
        }
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
