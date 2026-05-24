#!/usr/bin/env node
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import fetch from "node-fetch";

const WHATSAPP_TOKEN = process.env.META_ACCESS_TOKEN;
const PHONE_NUMBER_ID = process.env.META_WHATSAPP_ID;

if (!WHATSAPP_TOKEN || !PHONE_NUMBER_ID) {
  console.error("Faltan variables de entorno WHATSAPP_TOKEN o WHATSAPP_PHONE_NUMBER_ID");
  process.exit(1);
}

const server = new Server(
  {
    name: "sorsabsa-whatsapp",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "send_whatsapp_message",
        description: "Envía un mensaje de texto por WhatsApp usando la API de Meta Cloud",
        inputSchema: {
          type: "object",
          properties: {
            to: {
              type: "string",
              description: "Número de teléfono en formato internacional (ej: 593987654321)",
            },
            message: {
              type: "string",
              description: "El contenido del mensaje",
            },
          },
          required: ["to", "message"],
        },
      },
      {
        name: "send_whatsapp_template",
        description: "Envía un mensaje de plantilla (necesario para iniciar conversaciones)",
        inputSchema: {
          type: "object",
          properties: {
            to: {
              type: "string",
              description: "Número internacional (ej: 593987654321)",
            },
            template_name: {
              type: "string",
              description: "Nombre de la plantilla aprobada en Meta (ej: hello_world)",
            },
            language_code: {
              type: "string",
              description: "Código de idioma (ej: es, en_US)",
              default: "es"
            },
            components: {
              type: "array",
              description: "Variables dinámicas para la plantilla",
            }
          },
          required: ["to", "template_name"],
        },
      },
    ],
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "send_whatsapp_message") {
    const { to, message } = request.params.arguments;

    try {
      const response = await fetch(
        `https://graph.facebook.com/v22.0/${PHONE_NUMBER_ID}/messages`,
        {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${WHATSAPP_TOKEN}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            messaging_product: "whatsapp",
            to: to,
            type: "text",
            text: { body: message },
          }),
        }
      );

      const data = await response.json();
      if (!response.ok) throw new Error(JSON.stringify(data));

      return { content: [{ type: "text", text: `Mensaje enviado a ${to}. ID: ${data.messages[0].id}` }] };
    } catch (error) {
      return { content: [{ type: "text", text: `Error: ${error.message}` }], isError: true };
    }
  }

  if (request.params.name === "send_whatsapp_template") {
    const { to, template_name, language_code = "es", components = [] } = request.params.arguments;

    try {
      const response = await fetch(
        `https://graph.facebook.com/v22.0/${PHONE_NUMBER_ID}/messages`,
        {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${WHATSAPP_TOKEN}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            messaging_product: "whatsapp",
            to: to,
            type: "template",
            template: {
              name: template_name,
              language: { code: language_code },
              components: components
            }
          }),
        }
      );
      const data = await response.json();
      if (!response.ok) throw new Error(JSON.stringify(data));
      return { content: [{ type: "text", text: `Plantilla '${template_name}' enviada a ${to}. ID: ${data.messages[0].id}` }] };
    } catch (error) {
      return { content: [{ type: "text", text: `Error: ${error.message}` }], isError: true };
    }
  }
  throw new Error("Herramienta no encontrada");
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch(console.error);