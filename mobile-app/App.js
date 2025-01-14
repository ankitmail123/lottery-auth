import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, Button, Alert } from 'react-native';
import { Camera } from 'expo-camera';
import * as FileSystem from 'expo-file-system';
import { TicketVerifier } from './ticket_verifier';

// Initialize verifier with the same secret key as the server
const SECRET_KEY = 'your-secret-key-here';  // Change this in production
const verifier = new TicketVerifier(SECRET_KEY);

export default function App() {
  const [hasPermission, setHasPermission] = useState(null);
  const [scanning, setScanning] = useState(true);
  const [camera, setCamera] = useState(null);

  useEffect(() => {
    (async () => {
      const { status } = await Camera.requestCameraPermissionsAsync();
      setHasPermission(status === 'granted');
    })();
  }, []);

  const handleBarCodeScanned = async ({ data }) => {
    try {
      setScanning(false);

      // Take a picture of the QR code
      if (!camera) return;
      
      const photo = await camera.takePictureAsync({
        quality: 1,
        base64: false,
      });

      // Save image temporarily
      const tempFile = `${FileSystem.cacheDirectory}temp_qr.png`;
      await FileSystem.moveAsync({
        from: photo.uri,
        to: tempFile
      });

      // Verify the QR code
      const [isValid, result] = await verifier.verifyCompositeQR(tempFile);

      // Delete temp file
      await FileSystem.deleteAsync(tempFile);

      // Show result
      if (isValid) {
        Alert.alert(
          'Valid Ticket',
          `Ticket ID: ${result.ticket_id}\nDraw Date: ${result.draw_date}\nTicket Price: ${result.ticket_price}`,
          [{ text: 'OK', onPress: () => setScanning(true) }]
        );
      } else {
        Alert.alert(
          'Invalid Ticket',
          result,
          [{ text: 'OK', onPress: () => setScanning(true) }]
        );
      }

    } catch (error) {
      Alert.alert(
        'Error',
        error.message,
        [{ text: 'OK', onPress: () => setScanning(true) }]
      );
    }
  };

  if (hasPermission === null) {
    return <View style={styles.container}><Text>Requesting camera permission...</Text></View>;
  }
  if (hasPermission === false) {
    return <View style={styles.container}><Text>No access to camera</Text></View>;
  }

  return (
    <View style={styles.container}>
      <Camera
        ref={ref => setCamera(ref)}
        style={styles.camera}
        type={Camera.Constants.Type.back}
        onBarCodeScanned={scanning ? handleBarCodeScanned : undefined}
      >
        <View style={styles.overlay}>
          <View style={styles.scanArea} />
        </View>
      </Camera>
      <Button
        title={scanning ? "Stop Scanning" : "Start Scanning"}
        onPress={() => setScanning(!scanning)}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  camera: {
    flex: 1,
  },
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  scanArea: {
    width: 200,
    height: 200,
    borderWidth: 2,
    borderColor: '#fff',
    backgroundColor: 'transparent',
  },
});
