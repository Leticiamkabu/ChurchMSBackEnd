# generate an excel sheet from data
from fastapi import  Response
from openpyxl import Workbook
from io import BytesIO
from typing import Any
import os

# @router.post("/generate-excel/")
def generate_excel(data: Any, filename : str):
    """
    Generate an Excel file from any data.
    :param data: Data of any type (list, dictionary, etc.).
    :return: Excel file as a downloadable response.
    """
    # Create an Excel workbook and worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = filename

    print("work book created ", wb)
    print("work book is active ", ws)
    print("work book name ", ws.title)

    # Determine the structure of the data and process it
    if isinstance(data, list):
        print("am in the list ")
        if not data:
            raise HTTPException(status_code=400, detail="The list is empty.")
        if isinstance(data[0], dict):
            # List of dictionaries
            headers = list(data[0].keys())
            ws.append(headers)
            for row in data:
                ws.append(list(row.values()))
        else:
            # List of non-dictionary elements
            headers = ["Values"]
            ws.append(headers)
            for item in data:
                ws.append([item])

    elif isinstance(data, dict):
        print("am in the dict ")
        # Single dictionary
        headers = list(data.keys())
        ws.append(headers)
        ws.append(list(data.values()))

    else:
        print("am in the other type ", type(data))
        # Fallback for other types
        headers = ["Data"]
        ws.append(headers)
        ws.append([data])

    print("excel data ",wb)
    
    # Use the existing 'uploads' folder
    upload_folder_path = os.path.join(os.path.dirname(__file__), 'reports')

    # Ensure the 'uploads' directory exists (optional, in case it wasn't created)
    os.makedirs(upload_folder_path, exist_ok=True)

    # Define the path to save the file in your existing 'uploads' folder
    save_path = os.path.join(upload_folder_path, f"{filename}.xlsx")
    # Create a temporary file to save the workbook
    # temp_file_path = f"/tmp/{filename}.xlsx"  # You can change the path as needed
    wb.save(save_path)

    # output = BytesIO()
    # wb.save(output)
    # output.seek(0)

    # Create a response with the Excel file
    # response_headers = {
    #     'Content-Disposition': 'attachment; filename="data.xlsx"'
    # }
    # return Response(
    #     content=output.read(),
    #     media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    #     headers=response_headers
    # )

    return save_path