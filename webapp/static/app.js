function App() {
    const [ticketId, setTicketId] = React.useState('');
    const [qrCode, setQrCode] = React.useState(null);
    const [error, setError] = React.useState(null);
    const [loading, setLoading] = React.useState(false);
    const [ticketData, setTicketData] = React.useState(null);

    async function generateQR() {
        const ticketId = document.getElementById('ticketId').value.trim();
        if (!ticketId) {
            setError('Please enter a ticket ID');
            return;
        }

        try {
            setLoading(true);
            setError(null);
            document.getElementById('generateButton').disabled = true;
            document.getElementById('loader').style.display = 'flex';
            document.getElementById('qrCode').innerHTML = '';
            document.getElementById('actionButtons').style.display = 'none';

            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ ticketId }),
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to generate QR code');
            }

            setQrCode(data.qrData);
            setTicketData(data.ticketData);
        } catch (error) {
            console.error('Error:', error);
            setError(error.message || 'Error generating QR code');
            setQrCode(null);
            setTicketData(null);
        } finally {
            setLoading(false);
            document.getElementById('generateButton').disabled = false;
            document.getElementById('loader').style.display = 'none';
        }
    };

    function printQR() {
        const qrImage = document.querySelector('#qrCode img');
        if (!qrImage) {
            setError('No QR code to print');
            return;
        }

        const printWindow = window.open('', '', 'width=600,height=600');
        printWindow.document.write(`
            <html>
            <head>
                <title>Print QR Code</title>
                <style>
                    body {
                        margin: 0;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                    }
                    img {
                        width: 100mm;
                        height: 100mm;
                    }
                </style>
            </head>
            <body>
                <img src="${qrImage.src}" alt="QR Code">
            </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.focus();
        setTimeout(() => {
            printWindow.print();
            printWindow.close();
        }, 250);
    };

    async function copyQR() {
        const qrImage = document.querySelector('#qrCode img');
        if (!qrImage) {
            setError('No QR code to copy');
            return;
        }

        try {
            const canvas = document.createElement('canvas');
            canvas.width = qrImage.naturalWidth;
            canvas.height = qrImage.naturalHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(qrImage, 0, 0);
            
            const blob = await new Promise(resolve => canvas.toBlob(resolve));
            const item = new ClipboardItem({ 'image/png': blob });
            await navigator.clipboard.write([item]);
            
            // Show success message
            const originalText = document.getElementById('copyButton').textContent;
            document.getElementById('copyButton').textContent = 'Copied!';
            setTimeout(() => {
                document.getElementById('copyButton').textContent = originalText;
            }, 2000);
        } catch (error) {
            console.error('Error:', error);
            setError('Failed to copy QR code');
        }
    };

    React.useEffect(() => {
        document.getElementById('ticketId').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                generateQR();
            }
        });
    }, []);

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
                        id="generateButton"
                        onClick={generateQR}
                        disabled={loading || !ticketId}
                    >
                        {loading ? 'Generating...' : 'Generate QR'}
                    </button>
                    <div id="loader" className="spinner-border text-primary" role="status" style={{display: 'none'}}>
                        <span className="visually-hidden">Loading...</span>
                    </div>
                </div>
            </div>

            {error && (
                <div id="error" className="alert alert-danger" role="alert">
                    {error}
                </div>
            )}

            {qrCode && (
                <div className="text-center">
                    <div className="qr-container print-container">
                        <div id="qrCode">
                            <img
                                src={`data:image/png;base64,${qrCode}`}
                                alt="QR Code"
                            />
                        </div>
                    </div>
                    
                    <div id="actionButtons" className="btn-group">
                        <button className="btn btn-success me-2" onClick={printQR}>
                            Print QR
                        </button>
                        <button id="copyButton" className="btn btn-info" onClick={copyQR}>
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
