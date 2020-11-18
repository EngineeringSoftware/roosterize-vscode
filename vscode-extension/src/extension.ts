import * as net from "net";
import * as path from "path";
import * as vscode from 'vscode';

import { LanguageClient, LanguageClientOptions, ServerOptions } from "vscode-languageclient";

let client: LanguageClient;

function getClientOptions(): LanguageClientOptions {
    return {
        // Register the server for Coq documents
        documentSelector: [
            { scheme: "file", language: "coq" },
            { scheme: "untitled", language: "coq" },
        ],
        outputChannelName: "[roosterize] Server",
        synchronize: {
            // Watch out for .roosterizerc changes in the workspace
            fileEvents: vscode.workspace.createFileSystemWatcher("**/.roosterizerc"),
        }
    }
}

function startLangServerTCP(addr: number): LanguageClient {
    const serverOptions: ServerOptions = () => {
        return new Promise((resolve, reject) => {
            const clientSocket = new net.Socket();
            clientSocket.connect(addr, "127.0.0.1", () => {
                resolve({
                    reader: clientSocket,
                    writer: clientSocket,
                });
            });
        });
    };

    return new LanguageClient(`tcp lang server (port ${addr})`, serverOptions, getClientOptions());
}

function startLangServer(
    command: string, args: string[], cwd: string,
): LanguageClient {
    const serverOptions: ServerOptions = {
        args,
        command,
        options: { cwd },
    };

    return new LanguageClient(command, serverOptions, getClientOptions());
}

function isStartedInDebugMode(): boolean {
    return process.env.VSCODE_DEBUG_MODE == "true";
}

export function activate(context: vscode.ExtensionContext) {
    if (isStartedInDebugMode()) {
        // DEBUGGING: run server manually
        console.log("roosterize is in debug mode");
        client = startLangServerTCP(20145);
    } else {
        // Production: Start the server
        const cwd = path.join(__dirname, "..", "..");
        client = startLangServer("roosterize", ["vscode_server"], cwd);
    }

    context.subscriptions.push(client.start());

    console.log('"roosterize" is now alive!');
}

export function deactivate(): Thenable<void> {
    return client ? client.stop() : Promise.resolve();
}
