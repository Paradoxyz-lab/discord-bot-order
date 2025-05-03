from core.utils import load_data, save_data, get_priority

TEST_MODE = True

async def handle_join(member):
    data = load_data()
    main = data["main_list"]
    extra = data["extra_list"]
    max_main = data["max_main"]

    user_id = str(member.id)
    user_priority = get_priority(member)

    if user_id in main or user_id in extra:
        return "Вы уже зарегистрированы."

    if len(main) < max_main:
        main.append(user_id)
        save_data(data)
        return "Вы добавлены в основной список ✅"

    weakest = None
    weakest_priority = 99

    for uid in main:
        existing = await member.guild.fetch_member(int(uid))
        existing_priority = get_priority(existing)

        if user_priority > existing_priority:
            if existing_priority < weakest_priority:
                weakest = uid
                weakest_priority = existing_priority

    if weakest:
        main.remove(weakest)
        extra.append(weakest)
        main.append(user_id)
        save_data(data)
        return f"Вы вытеснили участника <@{weakest}> и заняли место в основном списке 🧠"

    extra.append(user_id)
    save_data(data)
    return "Основной список заполнен, вы добавлены в доп.слоты 📥"

def handle_leave(member):
    data = load_data()
    user_id = str(member.id)

    removed = False
    if user_id in data["main_list"]:
        data["main_list"].remove(user_id)
        removed = True
    if user_id in data["extra_list"]:
        data["extra_list"].remove(user_id)
        removed = True

    if removed:
        save_data(data)
        return "Вы успешно удалены из списка ❌"
    else:
        return "Вы не были зарегистрированы."