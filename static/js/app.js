document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-rating-picker]").forEach((picker) => {
    const input = document.getElementById(picker.dataset.inputId);
    const hint = picker.parentElement.querySelector("[data-rating-hint]");
    const buttons = [...picker.querySelectorAll("button")];
    const paint = (value) => {
      buttons.forEach((button) => button.classList.toggle("selected", Number(button.dataset.rating) <= value));
      if (hint) hint.textContent = value ? `${value} out of 5 stars` : "Select a rating";
    };
    buttons.forEach((button) => {
      button.addEventListener("click", () => {
        const value = Number(button.dataset.rating);
        input.value = value;
        paint(value);
      });
      button.addEventListener("mouseenter", () => paint(Number(button.dataset.rating)));
    });
    picker.addEventListener("mouseleave", () => paint(Number(input.value || 0)));
    paint(Number(input.value || 0));
  });

  document.querySelectorAll("[data-copy-target]").forEach((button) => {
    button.addEventListener("click", async () => {
      const target = document.getElementById(button.dataset.copyTarget);
      const value = target?.innerText || target?.textContent || "";
      try {
        await navigator.clipboard.writeText(value.trim());
        const original = button.textContent;
        button.textContent = button.classList.contains("icon-button") ? "✓" : "Copied!";
        setTimeout(() => { button.textContent = original; }, 1600);
      } catch (_) { window.prompt("Copy this text:", value.trim()); }
    });
  });

  document.querySelectorAll("[data-modal-open]").forEach((button) => button.addEventListener("click", () => {
    const modal = document.getElementById(button.dataset.modalOpen);
    modal?.classList.add("open");
    modal?.setAttribute("aria-hidden", "false");
  }));
  document.querySelectorAll("[data-modal-close]").forEach((button) => button.addEventListener("click", () => {
    const modal = button.closest(".modal-backdrop");
    modal?.classList.remove("open");
    modal?.setAttribute("aria-hidden", "true");
  }));
  document.querySelectorAll(".modal-backdrop").forEach((modal) => modal.addEventListener("click", (event) => {
    if (event.target === modal) { modal.classList.remove("open"); modal.setAttribute("aria-hidden", "true"); }
  }));
});
