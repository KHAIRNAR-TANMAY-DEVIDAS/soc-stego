# Integrate Steganography Tool into SOC Stego

The goal is to expand the existing SOC Steganalysis Detection Tool by adding a built-in Steganography tool. This new tool will allow users to encode and decode secret messages or scripts within images. Additionally, it will feature an optional password-based encryption and decryption layer. The main GUI will be restructured to offer two primary modes: "Steganography" and "Steganalysis".

## User Review Required

> [!IMPORTANT]
> **GUI Layout Choice:** To provide the two main options ("Steganography" and "Steganalysis"), we can either:
> 1.  **Top-Level Tabs:** Add a top-level Tab View (e.g., Tab 1: Steganography, Tab 2: Steganalysis).
> 2.  **Home Screen Navigation:** Create a "Home/Launch" screen with two large buttons that transition the window into the respective tool's interface. 
> *I have planned for Option 1 (Top-level Tab View) as it's cleaner for quick switching, but let me know if you prefer Option 2!*

> [!IMPORTANT]
> **Encryption Standard:** The plan uses robust AES encryption (via the `cryptography` library) for the password protection feature. Alternatively, we could use a simpler XOR encryption. *Are you okay with adding the `cryptography` library to dependencies for better security?*

## Open Questions

- What specific image formats do you want to ensure are fully supported for *encoding*? (Note: Lossy formats like JPEG will destroy LSB steganography data when saved. PNG or BMP are strongly recommended for the *output* encoded image. We can accept any image as input, but the output will be saved as a lossless format like PNG).

## Proposed Changes

---

### Phase 1: Core Steganography Engine Development

We will create the backend logic for hiding and retrieving data, along with encryption.

#### [NEW] `core/stego_tool_engine.py`
- `encode_message(image_path, secret_message, output_path, password=None)`: 
  - Optionally encrypts the `secret_message` using the `password`.
  - Embeds the (encrypted) message into the image using LSB (Least Significant Bit) manipulation.
  - Saves the resulting image to `output_path` (enforced as PNG/lossless).
- `decode_message(image_path, password=None)`:
  - Extracts the hidden LSB data from the image.
  - If a `password` is provided, decrypts the extracted data.
  - Returns the hidden message/script.

#### [MODIFY] `requirements.txt`
- Add `cryptography` library to handle secure password-based encryption/decryption (if AES is chosen).

---

### Phase 2: GUI Restructuring

We will modify the main window to accommodate the two distinct tools under one roof.

#### [MODIFY] `gui/main_window.py`
- Modify `create_main_interface()` to introduce a primary `ctk.CTkTabview` for switching between the "Steganography Tool" and "Steganalysis Tool".
- Move the existing "Single Image Analysis" and "Batch Directory Analysis" tabs under the new "Steganalysis Tool" section.
- Initialize the layout for the new "Steganography Tool" section.

---

### Phase 3: Steganography GUI Implementation

We will build the frontend interface for encoding and decoding messages.

#### [MODIFY] `gui/main_window.py`
- **Encode Interface**: 
  - File selection for input image.
  - Text area for the secret message/script.
  - Optional password entry field.
  - File save dialog to choose the output image destination.
  - "Encode" button with a progress/status indicator.
- **Decode Interface**: 
  - File selection for the target stego-image.
  - Optional password entry field.
  - "Decode" button.
  - Text area to display the extracted message/script.

---

### Phase 4: Integration and Polish

- Connect the UI buttons in the Steganography tabs to the `core/stego_tool_engine.py` functions using multi-threading to prevent GUI freezing.
- Add informative status messages, success dialogs, and error handling for incorrect passwords or missing hidden data.

## Verification Plan

### Automated/Local Tests
- Encode a sample text string into `test_dummy.png` with a password.
- Attempt to decode it with the correct password (verify success).
- Attempt to decode it with an incorrect password (verify handled failure).

### Manual Verification
- Launch the GUI and verify the new top-level structure ("Steganography" vs "Steganalysis").
- Test the Steganography "Encode" tab by hiding a script in an image and saving it.
- Switch to the "Steganalysis" tab and analyze the newly created image to ensure the existing tool successfully flags it as anomalous/containing a payload.
