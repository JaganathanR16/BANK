# app.py

from flask import Flask, render_template, request, send_file
from datetime import datetime
import calendar
from io import BytesIO

# PDF 22222
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4

app = Flask(__name__)

# STORE RESULT FOR PDF
latest_result = ""


# -----------------------------------
# LEAP YEAR CHECK
# -----------------------------------
def is_leap_year(year):

    return calendar.isleap(year)


# -----------------------------------
# HOME PAGE
# -----------------------------------
@app.route("/", methods=["GET", "POST"])
def index():

    global latest_result

    result = ""

    principal = ""

    loan_from = ""

    loan_to = ""

    from_dates = []

    to_dates = []

    rates = []

    try:

        if request.method == "POST":

            # GET VALUES
            principal = request.form.get(
                "principal",
                ""
            )

            loan_from = request.form.get(
                "loan_from",
                ""
            )

            loan_to = request.form.get(
                "loan_to",
                ""
            )

            from_dates = request.form.getlist(
                "from_date[]"
            )

            to_dates = request.form.getlist(
                "to_date[]"
            )

            rates = request.form.getlist(
                "rate[]"
            )

            # CONVERT VALUES
            principal_value = float(
                principal
            )

            loan_from_date = datetime.strptime(
                loan_from,
                "%Y-%m-%d"
            )

            loan_to_date = datetime.strptime(
                loan_to,
                "%Y-%m-%d"
            )

            # VALIDATE
            if loan_from_date > loan_to_date:

                result = (
                    "ERROR : Loan From Date "
                    "cannot be greater than "
                    "Loan To Date."
                )

            else:

                total_interest = 0

                result += (
                    "\nINTEREST CALCULATION DETAILS\n"
                )

                result += "=" * 90 + "\n"

                valid_set_found = False

                # LOOP ROWS
                for i in range(len(from_dates)):

                    if (
                        from_dates[i].strip() == "" or
                        to_dates[i].strip() == "" or
                        rates[i].strip() == ""
                    ):
                        continue

                    set_from = datetime.strptime(
                        from_dates[i],
                        "%Y-%m-%d"
                    )

                    set_to = datetime.strptime(
                        to_dates[i],
                        "%Y-%m-%d"
                    )

                    rate = float(
                        rates[i]
                    )

                    # VALIDATE SET DATES
                    if set_from > set_to:

                        result += (
                            f"\nERROR : "
                            f"Interest Set {i+1} "
                            f"From Date cannot be "
                            f"greater than To Date.\n"
                        )

                        continue

                    # OVERLAP
                    calc_from = max(
                        loan_from_date,
                        set_from
                    )

                    calc_to = min(
                        loan_to_date,
                        set_to
                    )

                    if calc_from <= calc_to:

                        valid_set_found = True

                        # DAYS
                        noof_days = (
                            calc_to - calc_from
                        ).days + 1

                        # LEAP YEAR
                        days_in_year = (
                            366
                            if is_leap_year(
                                calc_from.year
                            )
                            else 365
                        )

                        # INTEREST
                        interest = (
                            noof_days *
                            principal_value *
                            rate
                        ) / (
                            100 * days_in_year
                        )

                        total_interest += interest

                        # DISPLAY
                        result += (
                            f"\nINTEREST SET : {i+1}\n"
                        )

                        result += (
                            "-" * 90 + "\n"
                        )

                        result += (
                            f"Interest Set Period : "
                            f"{set_from.strftime('%d-%m-%Y')} "
                            f"TO "
                            f"{set_to.strftime('%d-%m-%Y')}\n"
                        )

                        result += (
                            f"Applicable Period  : "
                            f"{calc_from.strftime('%d-%m-%Y')} "
                            f"TO "
                            f"{calc_to.strftime('%d-%m-%Y')}\n"
                        )

                        result += (
                            f"Number Of Days     : "
                            f"{noof_days}\n"
                        )

                        result += (
                            f"Principal Amount   : "
                            f"Rs {principal_value:,.2f}\n"
                        )

                        result += (
                            f"Interest Rate      : "
                            f"{rate}%\n"
                        )

                        result += (
                            f"Days In Year       : "
                            f"{days_in_year}\n"
                        )

                        result += (
                            "\nFORMULA:\n"
                        )

                        result += (
                            f"({noof_days} x "
                            f"{principal_value:,.2f} x "
                            f"{rate}) / "
                            f"(100 x {days_in_year})\n"
                        )

                        result += (
                            f"\nINTEREST AMOUNT : "
                            f"Rs {interest:,.2f}\n"
                        )

                        result += (
                            "=" * 90 + "\n"
                        )

                # NO MATCH
                if not valid_set_found:

                    result += (
                        "\nNo matching interest "
                        "set found.\n"
                    )

                # TOTALS
                total_amount = (
                    principal_value +
                    total_interest
                )

                result += (
                    f"\nTOTAL INTEREST : "
                    f"Rs {total_interest:,.2f}\n"
                )

                result += (
                    f"TOTAL AMOUNT   : "
                    f"Rs {total_amount:,.2f}\n"
                )

                # SAVE FOR PDF
                latest_result = result

    except ValueError:

        result = (
            "ERROR : Please enter "
            "correct values."
        )

    except Exception as e:

        result = (
            f"ERROR : {str(e)}"
        )

    return render_template(
        "index.html",
        result=result,
        principal=principal,
        loan_from=loan_from,
        loan_to=loan_to,
        from_dates=from_dates,
        to_dates=to_dates,
        rates=rates
    )


# -----------------------------------
# DOWNLOAD PDF
# -----------------------------------
@app.route("/download_pdf")
def download_pdf():

    global latest_result

    if latest_result.strip() == "":

        return "No result available."

    # MEMORY BUFFER
    buffer = BytesIO()

    # CREATE PDF
    pdf = Canvas(
        buffer,
        pagesize=A4
    )

    width, height = A4

    y = height - 50

    # TITLE
    pdf.setFont(
        "Helvetica-Bold",
        16
    )

    pdf.drawString(
        50,
        y,
        "Interest Calculation Result"
    )

    y -= 30

    # FONT
    pdf.setFont(
        "Courier",
        10
    )

    lines = latest_result.split("\n")

    for line in lines:

        if y <= 40:

            pdf.showPage()

            pdf.setFont(
                "Courier",
                10
            )

            y = height - 50

        pdf.drawString(
            40,
            y,
            line[:140]
        )

        y -= 15

    # SAVE PDF
    pdf.save()

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="Interest_Result.pdf",
        mimetype="application/pdf"
    )


# -----------------------------------
# RUN APPLICATION
# -----------------------------------
if __name__ == "__main__":

    app.run(
        debug=True
    )