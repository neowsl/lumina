// NOTE: run the following file in browser devtools console

const targets = [];

const nodes = document.querySelectorAll("a.tabliscel-flex");
for (const node of nodes) {
    const rawText = node.innerText.trim();

    if (rawText.startsWith("Section")) {
        const cleanTitle = rawText.split("\n")[0].trim();

        targets.push({
            title: cleanTitle,
            url: node.href,
            id: node.href.split("/").pop(),
        });
    }
}

console.log(JSON.stringify(targets, null, 4));

// NOTE: copy the output into `data/sections.json`
