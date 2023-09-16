export function listenForOutsideClicks(
  listening: boolean,
  setListening: (value: boolean) => void,
  menuRef: React.RefObject<HTMLElement>,
  setIsOpen: (value: boolean) => void
) {
  return () => {
    if (listening) return;
    if (!menuRef.current) return;
    setListening(true);
    [`click`, `touchstart`].forEach((type) => {
      document.addEventListener(`click`, (evt) => {
        if (!menuRef.current || !evt.target) {
          return;
        }
        if (menuRef.current.contains(evt.target as Node)) return;
        setIsOpen(false);
      });
    });
  };
}
