document.addEventListener("DOMContentLoaded", function () {
  // Intersection Observerの設定
  const options = {
    root: null, // ビューポートをルートとして使用
    rootMargin: "50px", // 要素が表示される50px手前で読み込み開始
    threshold: 0.1, // 要素が10%表示されたときにコールバックを実行
  };

  // 遅延読み込みのコールバック関数
  const handleIntersection = (entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const img = entry.target;
        const src = img.getAttribute("data-src");

        if (src) {
          img.src = src;
          img.removeAttribute("data-src");
          img.classList.add("loaded");
        }

        observer.unobserve(img);
      }
    });
  };

  // Intersection Observerのインスタンスを作成
  const observer = new IntersectionObserver(handleIntersection, options);

  // 遅延読み込み対象の画像を監視
  document.querySelectorAll("img[data-src]").forEach((img) => {
    observer.observe(img);
  });
});
