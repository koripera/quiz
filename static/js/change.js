//絞り込みの入力欄について

const floatBtn = document.getElementById('floatBtn');
const searchPanel = document.getElementById('change');

floatBtn.addEventListener('click', () => {
searchPanel.classList.toggle('open');
});

// パネル外クリックで閉じる
document.addEventListener('click', (e) => {
if (!searchPanel.contains(e.target) && e.target !== floatBtn) {
  searchPanel.classList.remove('open');
}
});
