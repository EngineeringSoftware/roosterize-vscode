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

function isStartedInStandaloneMode(): boolean {
    return process.env.STANDALONE_SERVER == "true";
}

function restartClient(context: vscode.ExtensionContext) {
    if (client) {
        client.stop()
    }

    if (isStartedInStandaloneMode()) {
        // DEBUGGING: run server manually
        console.log("roosterize server should be started manually (`roosterize vscode_server --tcp`)");
        client = startLangServerTCP(20145);
    } else {
        // Production: Start the server
        const binPath = vscode.workspace.getConfiguration().get<string>("roosterize.binPath", "");
        client = startLangServer(
            binPath,
            ["vscode_server"], 
            path.join(binPath, ".."),
        );
    }

    context.subscriptions.push(client.start());

    console.log('"roosterize" is now alive!');
}

export function activate(context: vscode.ExtensionContext) {
    restartClient(context);

    // Listen to binPath changes
    vscode.workspace.onDidChangeConfiguration(
        (e) => {
            if (e.affectsConfiguration("roosterize.binPath")) {
                restartClient(context);
            }
        }
    );
}

export function deactivate(): Thenable<void> {
    return client ? client.stop() : Promise.resolve();
}
