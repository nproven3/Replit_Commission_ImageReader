import pytesseract
import cv2
from PIL import Image
import csv
import os

Condition = False

def preprocess_image(image_path):
    # Load the image using OpenCV
    image = cv2.imread(image_path)

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to improve text visibility
    _, threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Convert back to PIL Image
    return Image.fromarray(threshold)

def detect_text(image_path, roi_coordinates, header, filename):
    global Condition
    try:
        # Preprocess the image using OpenCV
        image = preprocess_image(image_path)

        # Perform OCR on the full image
        full_text = pytesseract.image_to_string(image, lang='eng')

        # Check if the "Price" parameter contains anything other than numbers or decimal values
        price_roi_x1, price_roi_y1, price_roi_x2, price_roi_y2 = roi_coordinates[2]
        price_roi_image = image.crop((price_roi_x1, price_roi_y1, price_roi_x2, price_roi_y2))
        price_text = pytesseract.image_to_string(price_roi_image, lang='eng')

        if not all(char.isdigit() or char == '.' or char == '\n' for char in price_text):
            print("TEST TEST TEST") ##This is what determines the type of image
            Condition = True

        # Extract values for each cell
        values = []
        for x1, y1, x2, y2 in roi_coordinates:
            roi_image = image.crop((x1, y1, x2, y2))
            roi_text = pytesseract.image_to_string(roi_image, lang='eng')

            if header[len(values)] == "Change":
                # Extract the number after the first + or - symbol and stop at the second + or - symbol
                change_value = "N/A"
                for word in roi_text.split():
                    if word.startswith("+") or word.startswith("-"):
                        change_value = word
                        break
                values.append(change_value)
            elif header[len(values)] == "%Change":
                # Extract the number after the second + or - symbol and stop after the percent sign
                percent_change_value = "N/A"
                count = 0
                for word in roi_text.split():
                    if word.startswith("+") or word.startswith("-"):
                        count += 1
                        if count == 2:
                            percent_change_value = word
                            break
                values.append(percent_change_value)
            elif header[len(values)] == "Exchange":
                # Extract only the last word from the Exchange field
                exchange_words = roi_text.split()
                last_word = exchange_words[-1] if exchange_words else "N/A"
                values.append(last_word)
            elif header[len(values)] == "High":
                # Extract the number before the "-" symbol
                high_value = "N/A"
                for word in roi_text.split():
                    if "-" in word:
                        high_value = word.split("-")[0]
                        break
                values.append(high_value)
            elif header[len(values)] == "Low":
                # Extract the number after the "-" symbol
                low_value = "N/A"
                for word in roi_text.split():
                    if "-" in word:
                        low_value = word.split("-")[1]
                        break
                values.append(low_value)
            else:
                # Replace any newline characters with spaces to make the value single-line
                values.append(roi_text.replace('\n', ' '))

        # Append the filename to the end of the row
        values.append(filename)

        # Save data to CSV
        with open("CSV Folder\\output.csv", "a", newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(values)

    except Exception as e:
        print("Error:", str(e))

if __name__ == "__main__":
    # Replace 'path/to/your/image.png' with the actual path to your image file.
    image_folder = r'UserFolder'

    default_roi_coordinates = [(x, y, x + w, y + h) for x, y, w, h in [
        # Define the coordinates (x, y, width, height) of each region of interest (ROI) for each cell in the CSV file
        (120, 100, 200, 100),  # ROI for Symbol
        (120, 180, 900, 100),  # ROI for Exchange
        (50, 280, 600, 150),  # ROI for Price
        # ... (other ROI coordinates)
    ]]

    # Open the CSV file once
    with open("CSV Folder\\output.csv", "w", newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        # Write the header to the CSV file
        header = [
            "Symbol", "Exchange", "Price", "Change", "%Change", "High", "Low", "52-Week High", "52-Week Low", "Open",
            "Previous-Close", "EPS(TTM)", "BVPS", "P/E(TTM)", "P/E(FWD)", "P/B", "P/S", "VOLUME", "%RANGE", "%TURNOVER",
            "DIVIDEND",
            "DIV YIELD", "NEXT EARNINGS", "EX-DIV DATE", "MARKET CAP", "TURNOVER", "AVG VOL (3M)", "SHARES OUTSTANDING", "LOT SIZE",
            "BETA", "FREE FLOAT MKT CAP", "FREE FLOAT", "FILE NAME"  # Add other headers for different cells...
        ]
        csvwriter.writerow(header)

    for filename in os.listdir(image_folder):
        image_path = os.path.join(image_folder, filename)

        Condition = False

        # Preprocess the image using OpenCV
        image = preprocess_image(image_path)

        # Define ROI coordinates for each cell
        # ...

        # Perform OCR on the full image
        full_text = pytesseract.image_to_string(image, lang='eng')

        # Check if the "Price" parameter contains anything other than numbers or decimal values
        price_roi_x1, price_roi_y1, price_roi_x2, price_roi_y2 = default_roi_coordinates[2]
        price_roi_image = image.crop((price_roi_x1, price_roi_y1, price_roi_x2, price_roi_y2))
        price_text = pytesseract.image_to_string(price_roi_image, lang='eng')

        if not all(char.isdigit() or char == '.' or char == '\n' for char in price_text):
            print("TEST TEST TEST")  # This is what determines the type of image
            Condition = True

        if Condition is False:
            # Define ROI coordinates for Condition False
            roi_coordinates = [(x, y, x + w, y + h) for x, y, w, h in [
                # Define the coordinates (x, y, width, height) of each region of interest (ROI) for each cell in the CSV file
                # Define the coordinates (x, y, width, height) of each region of interest (ROI) for each cell in the CSV file
                (120, 100, 200, 100),  # ROI for Symbol
                (50, 180, 900, 100),  # ROI for Exchange
                (50, 280, 600, 150),  # ROI for Price
                (100, 420, 400, 100),  # ROI for Change
                (100, 420, 400, 100),  # ROI for %Change
                (1010, 280, 325, 100),  # ROI for High
                (1010, 280, 325, 100),  # ROI for Low
                (500, 640, 400, 100),  # ROI for 52-Week High
                (500, 790, 400, 100),  # ROI for 52-Week Low
                (0, 640, 400, 100),  # ROI for Open
                (0, 790, 400, 100),  # ROI for Prev Close
                (0, 940, 400, 100),  # ROI for EPS(TTM)
                (0, 1090, 400, 100),  # ROI for BVPS
                (0, 1250, 400, 100),  # ROI for P/E(TTM)
                (0, 1400, 400, 100),  # ROI for P/E(FWD)
                (0, 1550, 400, 100),  # ROI for P/B
                (0, 1700, 400, 100),  # ROI for P/S
                (30, 30, 30, 30),  # ROI for VOLUME
                (500, 940, 400, 100),  # ROI for %RANGE
                (500, 1090, 400, 100),  # ROI for %TURNOVER
                (500, 1250, 400, 100),  # ROI for %DIVIDEND
                (500, 1400, 400, 100),  # ROI for DIV YIELD
                (500, 1550, 400, 100),  # ROI for NEXT EARNINGS
                (500, 1700, 400, 100),  # ROI for EX-DIV DATE
                (30, 30, 30, 30),           # ROI for MARKET CAP
                (1030, 640, 400, 100),  # ROI for TURNOVER
                (1030, 790, 400, 100),  # ROI for AVG VOL (3M)
                (1030, 940, 400, 100),  # ROI for SHARES OUTSTANDING
                (1200, 1090, 200, 100),  # ROI for LOT SIZE
                (1030, 1250, 400, 100),  # ROI for BETA
                (1030, 1400, 400, 100),  # ROI for FREE FLOAT MKT CAP
                (940, 1550, 500, 100),  # ROI for FREE FLOAT
                # Continue adding ROI coordinates for other cells...
                # ... (other ROI coordinates)
            ]]

        else:
            # Define ROI coordinates for Condition True
            roi_coordinates = [(x, y, x + w, y + h) for x, y, w, h in [
                # Define the coordinates (x, y, width, height) of each region of interest (ROI) for each cell in the CSV file
                (120, 100, 200, 100),  # ROI for Symbol
                (50, 180, 900, 100),  # ROI for Exchange
                (50, 250, 350, 300),  # ROI for Price
                (400, 250, 350, 300),  # ROI for Change
                (400, 250, 350, 300),  # ROI for %Change
                (50, 750, 500, 100),  # ROI for High
                (50, 750, 500, 100),  # ROI for Low
                (500, 950, 500, 100),  # ROI for 52-WEEK HIGH
                (500, 1150, 500, 100),  # ROI for 52-Week Low
                (50, 950, 500, 100),  # ROI for Open
                (50, 1150, 500, 100),  # ROI for Prev Close
                (50, 1350, 500, 100),  # ROI for EPS(TTM)
                (50, 1550, 500, 100),  # ROI for BVPS
                (50, 1750, 500, 100),  # ROI for P/E(TTM)
                (50, 1950, 500, 100),  # ROI for P/E(FWD)
                (50, 2150, 500, 100),  # ROI for P/B
                (50, 2350, 500, 100),  # ROI for P/S
                (500, 750, 500, 100),  # ROI for VOLUME
                (500, 1350, 500, 100),  # ROI for %RANGE
                (500, 1550, 500, 100),  # ROI for %TURNOVER
                (500, 1750, 500, 100),  # ROI for %DIVIDEND
                (500, 1950, 400, 100),  # ROI for DIV YIELD
                (500, 2150, 400, 100),  # ROI for NEXT EARNINGS
                (500, 2350, 400, 100),  # ROI for EX-DIV DATE
                (1030, 750, 400, 100),  # ROI for MARKET CAP
                (1030, 950, 400, 100),  # ROI for TURNOVER
                (1030, 1150, 400, 100),  # ROI for AVG VOL (3M)
                (1030, 1350, 400, 100),  # ROI for SHARES OUTSTANDING
                (1200, 1550, 200, 100),  # ROI for LOT SIZE
                (1030, 1750, 400, 100),  # ROI for BETA
                (1030, 1950, 400, 100),  # ROI for FREE FLOAT MKT CAP
                (940, 2150, 500, 100),  # ROI for FREE FLOAT
                # Continue adding ROI coordinates for other cells...
                # ... (other ROI coordinates)
            ]]

        # Define header for the CSV file

        detect_text(image_path, roi_coordinates, header, filename)
    print(Condition)