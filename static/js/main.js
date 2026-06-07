/**
 * TechSolutions — клиентские скрипты
 */

document.addEventListener("DOMContentLoaded", function () {
    // Эффект тени навбара при прокрутке
    const nav = document.getElementById("mainNav");
    if (nav) {
        const onScroll = () => {
            if (window.scrollY > 40) {
                nav.classList.add("scrolled");
            } else {
                nav.classList.remove("scrolled");
            }
        };
        window.addEventListener("scroll", onScroll, { passive: true });
        onScroll();
    }

    // Автоскрытие flash-сообщений через 5 секунд
    document.querySelectorAll(".flash-container .alert").forEach((alert) => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

    // Плавное появление карточек при скролле
    const cards = document.querySelectorAll(".case-card, .feature-card");
    if ("IntersectionObserver" in window && cards.length) {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.style.opacity = "1";
                        entry.target.style.transform = "translateY(0)";
                        observer.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.1, rootMargin: "0px 0px -40px 0px" }
        );

        cards.forEach((card) => {
            card.style.opacity = "0";
            card.style.transform = "translateY(24px)";
            card.style.transition = "opacity 0.5s ease, transform 0.5s ease";
            observer.observe(card);
        });
    }
});
