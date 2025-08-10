//phrase問題の折りたたみ部を開くタイミングで取得する

document.addEventListener("DOMContentLoaded", () => {

  // detailsにイベントを付与する関数
  function setupLazyDetails(details) {
    if (details.dataset.initialized) return; // 二重登録防止
    details.dataset.initialized = "true";

    details.addEventListener("toggle", async () => {
      if (details.open && !details.dataset.loaded) {
        const id    = details.dataset.id;    // data-id
        const chara = details.dataset.chara; // data-chara
        const content = await fetchContent(id, chara);
        
        // detailsの中に追加（外に置く場合は afterend に変更）
        details.insertAdjacentHTML("beforeend", `${content}`);

        details.dataset.loaded = "true";
      }
    });

    // 初期状態で open 指定されている場合は即ロード
    if (details.open) {
      details.dispatchEvent(new Event("toggle"));
    }
  }

  // 初期にある .lazy にセット
  document.querySelectorAll(".lazy").forEach(setupLazyDetails);

  // MutationObserverで動的追加を監視
  const observer = new MutationObserver(mutations => {
    mutations.forEach(mutation => {
      mutation.addedNodes.forEach(node => {
        if (node.nodeType === 1) { // ELEMENT_NODE
          if (node.matches(".lazy")) {
            setupLazyDetails(node);
          }
          // 内部に .lazy が含まれている場合
          node.querySelectorAll?.(".lazy").forEach(setupLazyDetails);
        }
      });
    });
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
});

/**
 * 固定URLに POST して HTML を取得
 * @param {string} id - サーバーに送るID
 * @param {string} chara - サーバーに送るキャラ名
 * @returns {Promise<string>} - HTML文字列
 */
async function fetchContent(id, chara) {
  const url = "/load_P"; // 固定URL
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id, chara })
  });
  if (!res.ok) {
    throw new Error(`Fetch failed: ${res.status}`);
  }
  return await res.text();
}

