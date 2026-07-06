import io
import os
import zipfile
from dataclasses import dataclass


@dataclass
class UploadedFile:
    name: str
    data: bytes

    def to_bytes_io(self) -> io.BytesIO:
        stream = io.BytesIO(self.data)
        stream.name = self.name
        return stream


def extract_pdf_files(uploaded_files) -> list[UploadedFile]:
    if not uploaded_files:
        return []

    extracted: list[UploadedFile] = []

    for uploaded_file in uploaded_files:
        name = uploaded_file.name
        raw = uploaded_file.getvalue()

        if name.lower().endswith(".zip"):
            extracted.extend(_extract_pdf_files_from_zip(raw))
        elif name.lower().endswith(".pdf"):
            extracted.append(UploadedFile(name=name, data=raw))

    return extracted


def _extract_pdf_files_from_zip(raw_zip: bytes) -> list[UploadedFile]:
    files: list[UploadedFile] = []

    with zipfile.ZipFile(io.BytesIO(raw_zip), "r") as archive:
        for member in archive.namelist():
            lower_name = member.lower()
            if not lower_name.endswith(".pdf"):
                continue
            if lower_name.startswith("__macosx/") or "/__macosx/" in lower_name:
                continue
            files.append(
                UploadedFile(
                    name=os.path.basename(member),
                    data=archive.read(member),
                )
            )

    return files


def build_zip(files: list[tuple[str, bytes]]) -> bytes:
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_name, data in files:
            archive.writestr(file_name, data)
    return output.getvalue()
