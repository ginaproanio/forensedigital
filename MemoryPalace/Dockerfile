FROM python:3.11-slim
WORKDIR /app
# MemoryPalace es principalmente conocimiento (markdown)
# Usamos un loop infinito para mantener el servicio vivo como volumen
COPY . .
EXPOSE 8000
CMD ["tail", "-f", "/dev/null"]