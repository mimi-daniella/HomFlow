// Sound effects
const audio = {
  slide: new Audio(
    "https://cdn.freesound.org/previews/367/367997_6512973-lq.mp3"
  ),
  accept: new Audio(
    "https://cdn.freesound.org/previews/220/220166_4100837-lq.mp3"
  ),
  reject: new Audio(
    "https://cdn.freesound.org/previews/657/657950_6142149-lq.mp3"
  ),
};

// Modal + glitch logic
const popover = document.querySelector("#connectModal");
const actions = document.querySelector(".modal__actions");
const modalGlitch = document.querySelector(".modal__glitch");
let glitched;
let glitchClock;

const handleKeyPress = ({ key }) => {
  if (key === "Escape") {
    popover.dataset.action = "Cancel";
  } else if (key === "Enter" && !actions.matches(":focus-within")) {
    popover.dataset.action = "Proceed";
    popover.hidePopover();
  }
};

const kickOff = () => {
  glitchClock = setTimeout(
    () => {
      modalGlitch.style.setProperty("animation-name", "glitch");
      requestAnimationFrame(async () => {
        await Promise.allSettled(
          modalGlitch.getAnimations().map((a) => a.finished)
        );
        glitched = true;
        modalGlitch.style.removeProperty("animation-name");
        kickOff();
      });
    },
    !glitched ? 1500 : Math.random() * 10000 + 2000
  );
};

popover.addEventListener("toggle", async (event) => {
  if (event.newState === "open") {
    setTimeout(() => {
      audio.slide.currentTime = 0;
      audio.slide.play();
    }, 200);
    window.addEventListener("keydown", handleKeyPress);
    kickOff();
  } else {
    if (glitchClock !== undefined) clearTimeout(glitchClock);
    if (popover.dataset.action === "Proceed") {
      audio.accept.currentTime = 0;
      audio.accept.play();
    } else {
      audio.reject.currentTime = 0;
      audio.reject.play();
    }
    glitched = false;
    await Promise.allSettled(popover.getAnimations().map((a) => a.finished));
    window.removeEventListener("keydown", handleKeyPress);
    delete popover.dataset.action;
  }
});

actions.addEventListener("click", (event) => {
  if (event.target.tagName === "BUTTON") {
    popover.dataset.action = event.target.dataset.action;
  }
});

// Trigger with keyboard shortcut "C"
const connectButton = document.querySelector("#connectBtn");
const handleConnect = ({ key }) => {
  if (
    connectButton.matches('[data-upgrading="true"]') ||
    popover.matches(":popover-open")
  )
    return;
  if (key.toLowerCase() === "c") {
    connectButton.dataset.upgrading = true;
    requestAnimationFrame(async () => {
      await Promise.allSettled(
        connectButton.getAnimations({ subtree: true }).map((a) => a.finished)
      );
      popover.showPopover();
      delete connectButton.dataset.upgrading;
    });
  }
};
window.addEventListener("keydown", handleConnect);
