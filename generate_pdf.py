from fpdf import FPDF

GRAY_BG = (230, 230, 230)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BLUE = (0, 51, 102)
SECTION_BG = (0, 70, 127)


class PDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def title_block(self, text):
        self.set_fill_color(*DARK_BLUE)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 18)
        self.cell(0, 14, text, ln=True, align="C", fill=True)
        self.ln(4)

    def section_header(self, text):
        self.set_fill_color(*SECTION_BG)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 8, text, ln=True, fill=True)
        self.set_text_color(*BLACK)
        self.ln(2)

    def body_text(self, text, bold=False):
        self.set_font("Helvetica", "B" if bold else "", 10)
        self.set_text_color(*BLACK)
        self.multi_cell(0, 5, text)
        self.ln(1)

    def code_block(self, text):
        self.set_fill_color(*GRAY_BG)
        self.set_font("Courier", "", 8)
        self.set_text_color(30, 30, 30)
        margin = self.l_margin
        self.set_x(margin)
        self.multi_cell(0, 5, text, fill=True, border=0)
        self.set_text_color(*BLACK)
        self.ln(2)

    def kv_table(self, rows):
        col_w = [55, 125]
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(200, 220, 240)
        self.cell(col_w[0], 7, "Property", border=1, fill=True)
        self.cell(col_w[1], 7, "Value", border=1, fill=True, ln=True)
        self.set_font("Helvetica", "", 9)
        fill = False
        for k, v in rows:
            self.set_fill_color(245, 248, 252) if fill else self.set_fill_color(*WHITE)
            self.cell(col_w[0], 6, k, border=1, fill=True)
            self.cell(col_w[1], 6, v, border=1, fill=True, ln=True)
            fill = not fill
        self.ln(3)

    def bullet(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*BLACK)
        self.cell(6)
        self.multi_cell(0, 5, f"  * {text}")
        self.ln(1)

    def numbered_bullet(self, n, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*BLACK)
        self.cell(6)
        self.multi_cell(0, 5, f"  {n}. {text}")
        self.ln(1)

    def sub_header(self, text):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(0, 51, 102)
        self.cell(0, 6, text, ln=True)
        self.set_text_color(*BLACK)
        self.ln(1)


def build_pdf():
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_margins(15, 10, 15)

    # ── Title ──────────────────────────────────────────────────────────────
    pdf.title_block("Complete LocalStack Setup Guide (Windows PowerShell)")

    # ── Connection Details ─────────────────────────────────────────────────
    pdf.section_header("Connection Details")
    pdf.kv_table([
        ("Endpoint URL", "http://localhost:4566"),
        ("Region", "ap-northeast-1 (Tokyo)"),
        ("Access Key ID", "test"),
        ("Secret Access Key", "test"),
        ("S3 Bucket Name", "my-test-bucket"),
    ])

    # ── Prerequisites ──────────────────────────────────────────────────────
    pdf.section_header("Prerequisites")
    pdf.bullet("Install Docker Desktop: https://www.docker.com/products/docker-desktop/")
    pdf.bullet("Install AWS CLI: https://aws.amazon.com/cli/")
    pdf.bullet("Verify AWS CLI:  aws --version")
    pdf.ln(2)

    # ── Step 1 ─────────────────────────────────────────────────────────────
    pdf.section_header("Step 1 - Start LocalStack")

    pdf.sub_header("Free Version (localstack:3.0.0):")
    pdf.code_block(
        "docker run -d --name localstack_test \\\n"
        "  -e SERVICES=s3,ses \\\n"
        "  -e DEFAULT_REGION=ap-northeast-1 \\\n"
        "  -p 4566:4566 \\\n"
        "  localstack/localstack:3.0.0"
    )

    pdf.sub_header("Pro Version (requires license token):")
    pdf.code_block(
        "docker run -d --name localstack_test \\\n"
        "  -e SERVICES=s3,ses \\\n"
        "  -e DEFAULT_REGION=ap-northeast-1 \\\n"
        "  -e LOCALSTACK_AUTH_TOKEN=your-token-here \\\n"
        "  -p 4566:4566 \\\n"
        "  localstack/localstack:latest"
    )

    pdf.body_text("Verify running:")
    pdf.code_block("docker ps")

    # ── Step 2 ─────────────────────────────────────────────────────────────
    pdf.section_header("Step 2 - Configure AWS CLI Profile")
    pdf.code_block(
        "aws configure --profile localstack\n"
        "AWS Access Key ID:     test\n"
        "AWS Secret Access Key: test\n"
        "Default region name:   ap-northeast-1\n"
        "Default output format: json"
    )

    # ── Step 3 ─────────────────────────────────────────────────────────────
    pdf.section_header("Step 3 - S3 Commands")
    pdf.body_text("Set checksum env vars first (run every new PowerShell window):")
    pdf.code_block(
        '$env:AWS_REQUEST_CHECKSUM_CALCULATION="when_required"\n'
        '$env:AWS_RESPONSE_CHECKSUM_VALIDATION="when_required"'
    )

    pdf.body_text("Create bucket:")
    pdf.code_block(
        "aws --profile localstack --endpoint-url=http://localhost:4566 \\\n"
        "  s3 mb s3://my-test-bucket --region ap-northeast-1"
    )

    pdf.body_text("List buckets:")
    pdf.code_block(
        "aws --profile localstack --endpoint-url=http://localhost:4566 s3 ls"
    )

    pdf.body_text("Upload file:")
    pdf.code_block(
        "aws --profile localstack --endpoint-url=http://localhost:4566 \\\n"
        "  s3 cp testfile.txt s3://my-test-bucket/"
    )

    pdf.body_text("List files in bucket:")
    pdf.code_block(
        "aws --profile localstack --endpoint-url=http://localhost:4566 \\\n"
        "  s3 ls s3://my-test-bucket/"
    )

    pdf.body_text("Download file:")
    pdf.code_block(
        "aws --profile localstack --endpoint-url=http://localhost:4566 \\\n"
        "  s3 cp s3://my-test-bucket/testfile.txt downloaded.txt"
    )

    pdf.body_text("Delete file:")
    pdf.code_block(
        "aws --profile localstack --endpoint-url=http://localhost:4566 \\\n"
        "  s3 rm s3://my-test-bucket/testfile.txt"
    )

    # ── Step 4 ─────────────────────────────────────────────────────────────
    pdf.section_header("Step 4 - SES Commands")
    pdf.body_text("NOTE: Re-verify email every time LocalStack restarts!", bold=True)
    pdf.ln(1)

    pdf.sub_header("Free Version (SESv1):")
    pdf.body_text("Verify sender email:")
    pdf.code_block(
        "aws --profile localstack --endpoint-url=http://localhost:4566 \\\n"
        "  ses verify-email-identity \\\n"
        "  --email-address sender@example.com --region ap-northeast-1"
    )

    pdf.body_text("List identities:")
    pdf.code_block(
        "aws --profile localstack --endpoint-url=http://localhost:4566 \\\n"
        "  ses list-identities --region ap-northeast-1"
    )

    pdf.body_text("Send email:")
    pdf.code_block(
        "aws --profile localstack --endpoint-url=http://localhost:4566 \\\n"
        "  ses send-email \\\n"
        "  --from sender@example.com \\\n"
        '  --destination "ToAddresses=recipient@example.com" \\\n'
        '  --message "Subject={Data=Test Subject,Charset=UTF-8},'
        'Body={Text={Data=Hello from LocalStack,Charset=UTF-8}}" \\\n'
        "  --region ap-northeast-1"
    )

    pdf.body_text("Check send statistics:")
    pdf.code_block(
        "aws --profile localstack --endpoint-url=http://localhost:4566 \\\n"
        "  ses get-send-statistics --region ap-northeast-1"
    )

    pdf.sub_header("Pro Version (SESv2):")
    pdf.body_text("Verify sender email:")
    pdf.code_block(
        "aws --profile localstack --endpoint-url=http://localhost:4566 \\\n"
        "  sesv2 create-email-identity \\\n"
        "  --email-identity sender@example.com --region ap-northeast-1"
    )

    pdf.body_text("List identities:")
    pdf.code_block(
        "aws --profile localstack --endpoint-url=http://localhost:4566 \\\n"
        "  sesv2 list-email-identities --region ap-northeast-1"
    )

    pdf.body_text("Send email:")
    pdf.code_block(
        "aws --profile localstack --endpoint-url=http://localhost:4566 \\\n"
        "  sesv2 send-email \\\n"
        "  --from-email-address sender@example.com \\\n"
        '  --destination "ToAddresses=recipient@example.com" \\\n'
        '  --content "Simple={Subject={Data=Test Subject,Charset=UTF-8},'
        'Body={Text={Data=Hello,Charset=UTF-8}}}" \\\n'
        "  --region ap-northeast-1"
    )

    # ── Step 5 ─────────────────────────────────────────────────────────────
    pdf.section_header("Step 5 - Auto Init Script (init-aws.ps1)")
    pdf.body_text("Run this after every LocalStack start to restore S3 bucket and SES verified email:")
    pdf.code_block(
        "Start-Sleep -Seconds 5\n"
        '$env:AWS_REQUEST_CHECKSUM_CALCULATION="when_required"\n'
        '$env:AWS_RESPONSE_CHECKSUM_VALIDATION="when_required"\n'
        "aws --profile localstack --endpoint-url=http://localhost:4566 \\\n"
        "  s3 mb s3://my-test-bucket --region ap-northeast-1\n"
        "aws --profile localstack --endpoint-url=http://localhost:4566 \\\n"
        "  ses verify-email-identity \\\n"
        "  --email-address sender@example.com --region ap-northeast-1\n"
        'Write-Host "LocalStack initialized successfully!"'
    )

    # ── Step 6 ─────────────────────────────────────────────────────────────
    pdf.section_header("Step 6 - Docker Compose")
    pdf.code_block(
        "version: '3.8'\n"
        "services:\n"
        "  localstack:\n"
        "    image: localstack/localstack:3.0.0\n"
        "    container_name: localstack_test\n"
        "    ports:\n"
        '      - "4566:4566"\n'
        "    environment:\n"
        "      - SERVICES=s3,ses\n"
        "      - DEFAULT_REGION=ap-northeast-1\n"
        "      - AWS_DEFAULT_REGION=ap-northeast-1\n"
        "      - AWS_ACCESS_KEY_ID=test\n"
        "      - AWS_SECRET_ACCESS_KEY=test\n"
        "      - DEBUG=1\n"
        "    volumes:\n"
        "      - ./init-scripts:/etc/localstack/init/ready.d"
    )

    # ── Step 7 ─────────────────────────────────────────────────────────────
    pdf.section_header("Step 7 - .NET 8.0 Integration")

    pdf.sub_header("NuGet Packages:")
    pdf.code_block(
        "dotnet add package AWSSDK.S3\n"
        "dotnet add package AWSSDK.SimpleEmail\n"
        "dotnet add package AWSSDK.Extensions.NETCore.Setup"
    )

    pdf.sub_header("appsettings.Development.json:")
    pdf.code_block(
        "{\n"
        '  "AWS": {\n'
        '    "ServiceURL": "http://localhost:4566",\n'
        '    "Region": "ap-northeast-1",\n'
        '    "AccessKey": "test",\n'
        '    "SecretKey": "test",\n'
        '    "ForcePathStyle": true\n'
        "  },\n"
        '  "S3": { "BucketName": "my-test-bucket" },\n'
        '  "SES": { "SenderEmail": "sender@example.com" }\n'
        "}"
    )

    pdf.sub_header("Important .NET settings:")
    pdf.bullet("ForcePathStyle = true  (required for S3)")
    pdf.bullet("DisablePayloadSigning = true  (required for S3 uploads)")
    pdf.bullet("ChecksumAlgorithm = ChecksumAlgorithm.NONE  (required for S3 uploads)")
    pdf.ln(2)

    # ── Key Notes ──────────────────────────────────────────────────────────
    pdf.section_header("Key Notes")
    notes = [
        "Use localstack:3.0.0 for free - latest requires paid license",
        "SESv1 (ses commands) for free version",
        "SESv2 (sesv2 commands) for pro version",
        "LocalStack does NOT send real emails - simulates API only",
        "All data (S3, SES) is lost when container restarts",
        "Set checksum env vars in every new PowerShell window before S3 uploads",
        "No AWS account needed",
    ]
    for note in notes:
        pdf.bullet(note)
    pdf.ln(2)

    # ── Quick Start Checklist ──────────────────────────────────────────────
    pdf.section_header("Quick Start Checklist")
    steps = [
        "Open Docker Desktop",
        "Run: docker-compose up -d",
        "Run: docker ps  (verify healthy)",
        r"Run: .\init-aws.ps1  (create bucket + verify email)",
        "Set checksum env vars in PowerShell",
        "Start coding / testing!",
    ]
    for i, step in enumerate(steps, 1):
        pdf.numbered_bullet(i, step)

    pdf.output("localstack-setup-guide.pdf")
    print("PDF generated: localstack-setup-guide.pdf")


if __name__ == "__main__":
    build_pdf()
