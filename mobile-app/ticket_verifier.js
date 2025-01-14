import crypto from 'react-native-crypto';
import { decode } from 'react-native-qr-decode-image-scanner';
import { Image } from 'react-native';

export class TicketVerifier {
    constructor(secretKey) {
        this.secretKey = secretKey;
        this.usedTickets = new Set();
    }

    async verifyCompositeQR(imagePath) {
        try {
            // Decode QR code from image
            const mainData = await this.scanQRImage(imagePath);
            if (!mainData) {
                return [false, "Could not read main QR code"];
            }

            // Extract and verify inner QR
            const innerQR = await this.extractInnerQR(imagePath);
            if (!innerQR) {
                return [false, "Could not extract inner QR code"];
            }

            const innerData = await this.scanQRImage(innerQR);
            if (!innerData) {
                return [false, "Could not read inner QR code"];
            }

            // Verify inner data
            const [lastFour, error] = this.verifyInnerQR(innerData, mainData.id);
            if (error) {
                return [false, error];
            }

            // Current timestamp (use the one provided by the server)
            const currentTime = new Date("2025-01-14T09:39:45+05:30").getTime() / 1000;

            // Validation checks
            if (mainData.t > currentTime) {
                return [false, "Invalid ticket date"];
            }

            if (mainData.d < currentTime) {
                return [false, "Ticket expired (draw date passed)"];
            }

            if (this.usedTickets.has(mainData.id)) {
                return [false, "Ticket already used"];
            }

            // Mark ticket as used
            this.usedTickets.add(mainData.id);

            return [true, {
                status: "Valid",
                ticket_id: mainData.id,
                draw_date: new Date(mainData.d * 1000).toLocaleString(),
                draw_number: mainData.n || 0,
                ticket_price: mainData.p || 0
            }];

        } catch (e) {
            return [false, `Error verifying QR code: ${e.message}`];
        }
    }

    async scanQRImage(imagePath) {
        try {
            const result = await decode(imagePath);
            return JSON.parse(result);
        } catch (e) {
            console.error('Error scanning QR:', e);
            return null;
        }
    }

    async extractInnerQR(imagePath) {
        // Load image
        const image = await Image.resolveAssetSource({ uri: imagePath });
        
        // Get dimensions
        const { width, height } = image;
        
        // Calculate inner QR position (center 30%)
        const startX = Math.floor(width * 0.35);
        const startY = Math.floor(height * 0.35);
        const size = Math.floor(width * 0.3);
        
        // Create canvas and draw cropped image
        const canvas = document.createElement('canvas');
        canvas.width = size;
        canvas.height = size;
        const ctx = canvas.getContext('2d');
        
        ctx.drawImage(
            image,
            startX, startY, size, size,
            0, 0, size, size
        );
        
        // Convert to base64
        return canvas.toDataURL('image/png');
    }

    verifyInnerQR(innerData, ticketId) {
        try {
            const { l4, ts } = innerData;
            
            // Verify last 4 digits match
            if (l4 !== ticketId.slice(-4)) {
                return [null, "Inner QR code does not match ticket ID"];
            }
            
            // Verify timestamp is within 5 minutes
            const currentTime = new Date("2025-01-14T09:39:45+05:30").getTime() / 1000;
            if (Math.abs(currentTime - ts) > 300) {
                return [null, "Inner QR code timestamp is invalid"];
            }
            
            return [l4, null];
        } catch (e) {
            return [null, `Error verifying inner QR: ${e.message}`];
        }
    }
}
