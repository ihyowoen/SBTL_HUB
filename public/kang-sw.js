// 강차장 알림 서비스워커(R21) — 앱 밖에서 먼저 말 걸기.
//
// 원칙: **알림 전용** — fetch 핸들러가 없다. 페이지 로딩·캐시에 일절 관여하지 않으므로
// (이 앱의 첫 SW지만) 기존 새로고침·배포 동작을 바꾸지 않는다. 오프라인 캐시를 여기에
// 추가하지 말 것 — 캐시 계층은 별도 설계·검증 없이는 클라이언트를 굳힐 수 있다.
//
// 동작: periodicsync("kang-nudge", 브라우저 재량 — 보통 12시간+, 설치된 안드로이드
// 크롬 계열에서만)마다 cards.json 카드 수를 IDB의 지난 수와 비교해, 늘었으면 로컬
// 알림 한 번("밤사이 새 카드 N장"). 상세는 앱에 들어와서 강차장 인사가 말한다 —
// 밖에서는 노크만. 서버 푸시(iOS 포함)는 구독 저장소가 생기면 v2.

const DB_NAME = "kang";
const STORE = "kv";

function idbOpen() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, 1);
    req.onupgradeneeded = () => { req.result.createObjectStore(STORE); };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}
function idbGet(key) {
  return idbOpen().then((db) => new Promise((resolve, reject) => {
    const tx = db.transaction(STORE, "readonly").objectStore(STORE).get(key);
    tx.onsuccess = () => resolve(tx.result);
    tx.onerror = () => reject(tx.error);
  })).catch(() => undefined);
}
function idbSet(key, val) {
  return idbOpen().then((db) => new Promise((resolve, reject) => {
    const tx = db.transaction(STORE, "readwrite").objectStore(STORE).put(val, key);
    tx.onsuccess = () => resolve(true);
    tx.onerror = () => reject(tx.error);
  })).catch(() => false);
}

// 새 카드 확인 — periodicsync와 테스트 메시지가 같은 루틴을 쓴다(경로 이원화 금지).
// 반환값은 테스트 응답용 {count, prev, delta, notified}.
async function checkNewCards() {
  let count = null;
  try {
    const res = await fetch("/data/cards.json", { cache: "no-store" });
    if (!res.ok) return { error: "fetch " + res.status };
    const j = await res.json();
    const cards = (j && (j.cards || j)) || [];
    count = Array.isArray(cards) ? cards.length : null;
  } catch (e) {
    return { error: "fetch-fail" };
  }
  if (count == null) return { error: "no-count" };
  const prev = await idbGet("lastCount");
  await idbSet("lastCount", count);
  const delta = typeof prev === "number" ? count - prev : 0;
  let notified = false;
  // 첫 실행(prev 없음)은 기준선만 기록 — 과거 전체를 '새로 왔다'고 말하지 않는다
  if (typeof prev === "number" && delta > 0 && self.Notification && Notification.permission === "granted") {
    try {
      await self.registration.showNotification("강차장", {
        body: `밤사이 새 카드 ${delta}장 들어왔어 — 읽어두고 정리해뒀어. 들어와서 봐.`,
        icon: "/data/kang.png",
        badge: "/data/kang.png",
        tag: "kang-nudge", // 같은 태그로 갱신 — 노크가 쌓여 도배되지 않게
        data: { url: "/" },
      });
      notified = true;
    } catch (e) { /* 알림 실패는 조용히 — 다음 주기에 다시 */ }
  }
  return { count, prev: typeof prev === "number" ? prev : null, delta, notified };
}

self.addEventListener("install", () => { self.skipWaiting(); });
self.addEventListener("activate", (event) => { event.waitUntil(self.clients.claim()); });

self.addEventListener("periodicsync", (event) => {
  if (event.tag === "kang-nudge") event.waitUntil(checkNewCards());
});

// 앱에서 보내는 테스트/즉시 확인 — 같은 루틴을 돌리고 결과를 회신(설정 UI·E2E 관측용)
self.addEventListener("message", (event) => {
  if (!event.data || event.data.type !== "kang-sync-test") return;
  event.waitUntil((async () => {
    const result = await checkNewCards();
    try { if (event.source) event.source.postMessage({ type: "kang-sync-result", result }); } catch (e) { /* noop */ }
  })());
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  event.waitUntil((async () => {
    // 알림이 지목한 목적지로 — 포커스만 하면 다른 경로에 있던 창은 노크 내용과 다른
    // 화면을 보여준다(Codex #197 R4). 이미 그 주소면 navigate 생략(불필요한 SPA
    // 리로드로 화면 상태를 잃지 않게 — 현 앱은 단일 경로라 대부분 생략된다).
    const target = new URL((event.notification.data && event.notification.data.url) || "/", self.location.origin).href;
    const list = await self.clients.matchAll({ type: "window", includeUncontrolled: true });
    for (const c of list) {
      if ("focus" in c) {
        await c.focus();
        if (c.url !== target && "navigate" in c) { try { await c.navigate(target); } catch (e) { /* noop */ } }
        return;
      }
    }
    if (self.clients.openWindow) await self.clients.openWindow(target);
  })());
});
