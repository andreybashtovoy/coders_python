## Ссылка на бот: [@timeplayer_bot](https://t.me/timeplayer_bot)

## Технологии

Язык программирования: Python
Библиотека для работы с Telegram Bot Api: python-telegram-bot

# Описание бота

⏱ Этот бот поможет узнать, как много времени вы уделяете разным занятиям,вести соответствующую статистику, контролировать все ваши занятия. Этим самым он поможет вам существенно улучшить вашу продуктивность.

🧩 Идея бота проста: когда вы начинаете заниматься чем-угодно (учёба, спорт, курсы, игры и т.п.), вы запускаете соответствующее занятие в боте командой /start. Как только закончите занятие, останавливаете его в боте командой /stop.

💡 Данный способ позволит не только контролировать все ваши занятия, но и улучшить фокус над ними. Как только вы запускаете занятие в боте, этим самым вы отдаете и своему мозгу четкую команду, что вы сейчас начали заниматься каким-то конкретным занятием и нужно сконцентрироваться только на нём.

📊 Бот имеет большое количество команд, с помощью которых можно выводить различную статистику о вашей продуктивности в виде графиков и прочей визуализации.

👥 Огромным плюсом будет использовать бот в групповых чатах. Это позволит видеть не только свою статистику, а и статистику всех участников чата. Этим самым можно даже соревноваться между собой по времени, проведенным с пользой, либо же просто контролировать друг друга. В групповом чате с данным ботом появиться особая атмосфера саморазвития, появятся новые темы для общения.

💪🏻 Есть два вида мотивации: внешняя и внутренняя. Внутренняя рождается внутри, её контролирует только сам человек и её часто тяжело добиться. Внешняя же рождается под влиянием других людей или других источников. Данный бот и позволит вам создать внешнюю мотивацию. Особый эффект будет, если использовать его в групповых чатах. Осознавая то, что ваши действия могут видеть и другие пользователи, часто может появляться дополнительное желание действовать. Или же все участники чата могут соревноваться между собой в времени, проведенном с пользой.

# Команды

 /start - выводит меню для выбора занятия, которое вы хотите начать. Можно дописать к команде количество минут, чтобы занятие считалось начатым несколько минут назад (например, /start 10)
 /start_project - выводит меню для выбора проекта, который вы хотите начать.
 /stop - остановить занятие. Занятие можно остановить со штрафом, отняв несколько минут, командой /stop *количество минут*. Например, /stop 15 остановит задание и отнимет 15 минут от итоговой продолжительности.
 /add - если вы забыли запустить занятие, вы можете добавить время с помощью этой команды. Она выводит меню, где нужно выбрать занятие и время, которое нужно добавить/отнять. Есть возможность сразу же задать время, дописав количество минут к команде (например, /add 10)
 /stats - выводит статистику пользователя, вызвавшего меню. Можно посмотреть статистику другого пользователя, отправив эту команду в ответ на его сообщение, либо написав команду в следующем виде: /stats @username.
 /days - выводит меню, в которой можно посмотреть все занятия за любой отдельный день.
 /rating - рейтинг участников чата за разные периоды времени. Сразу выводит рейтинг за текущий день.
 /projects - управление проектами занятий пользователя.
 /activities - управления личными занятиями пользователя.
 /chat - активировать Premium в чате.
 /toggle_tag - включить/выключить теги каждый час.
 /ranks - звания всех участников чата.
 /status - узнать своё текущее занятие.
 /rating_graph - график изменения рейтинга всех участников чата в течении всего времени существования чата.
 /reset - сбросить или восстановить все занятия
 
 # Занятия
 
 🧩 Есть два типа занятий: занятия с пользой и без. Занятия с пользой учитываются во всех меню со статистикой и с рейтингом участников чата.Вторые же нужны просто, чтобы отследить время, которое уделяешь какому-то не очень полезному занятию (игры, фильмы и т.п.).

🎮 Каждому пользователю по умолчанию доступен набор стандартных занятий. Но есть также возможность создавать и свои занятия. Сделать это можно командой /activities, которая откроет меню для управления вашими личными занятиями. При создании занятия можно настроить его доступность (личное либо для всех участников чата), а также указать, будет ли время, уделенное этому занятию, считаться как полезное.

🎲 Запустить занятие можно командой /start, по которой откроется меню для выбора занятия, которое вы хотите начать. Чем чаще вы используете какое-то занятие, тем выше его кнопка в меню. Останавливать занятия можно командой /stop. Если дописать после команды количество минут, то команда остановит занятие со штрафом. Например, /stop 15 остановит задание и отнимет 15 минут от итоговой продолжительности.

🎯 Если вы забыли запустить занятие, можно добавить время к этому занятию командой /add. В появившемся меню нужно указать занятие и его продолжительность.

# Проекты

📂 К каждому занятию есть возможность создавать проекты. Сами проекты - это все то, на что можно разделить занятие.Например, сейчас я разрабатываю этого бота, у меня активно занятие "Кодинг", а проект связан конкретно с этим ботом. Или, например, если вы проходите курсы,у вас может быть активно занятие "Курсы", а проект - это название самого курса (Английский с тетей Любой, Программируем сковородки за час и т.п.).С другими занятиями так же, можно даже занятие "Игры" разделить на проекты, где проекты - это названия игр, в которые вы играете.

🗂 Используя проекты, вы можете отследить, сколько времени вы уделяете какому-то отдельному проекту (сколько времени я делал эту конкретную лабораторную, сколько времени я играл в эту игру и т.п.)

✏️ Управлять проектами можно используя команду /projects