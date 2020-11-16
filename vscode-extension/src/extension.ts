import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    console.log('"roosterize" is now alive!');

    const cmdConfig = vscode.commands.registerCommand('extension.roosterize.config', () => {
        // TODO
        vscode.window.showInformationMessage('TODO config!');
    });
    const cmdSuggestNaming = vscode.commands.registerCommand('extension.roosterize.suggest_naming', () => {
        // TODO
        vscode.window.showInformationMessage('TODO suggest naming!');
    });
    const cmdDownloadModel = vscode.commands.registerCommand('extension.roosterize.download_model', () => {
        // TODO
        vscode.window.showInformationMessage('TODO download model!');
    });
    const cmdImproveModel = vscode.commands.registerCommand('extension.roosterize.improve_model', () => {
        // TODO
        vscode.window.showInformationMessage('TODO improve model!');
    });

    context.subscriptions.push(cmdConfig);
    context.subscriptions.push(cmdSuggestNaming);
    context.subscriptions.push(cmdDownloadModel);
    context.subscriptions.push(cmdImproveModel);
}
