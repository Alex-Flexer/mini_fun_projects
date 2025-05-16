from server import Server, Request, FileResponse, JsonResponse


server = Server("localhost", 8081)


def handler_home_page() -> FileResponse:
    return FileResponse("static/index.html", status=200)


def handler_create_user(request: Request) -> JsonResponse:
    body = request.body
    name = body.get("name", "NaN")
    age = body.get("age", "NaN`")
    print(f"{name} is {age} years old.")
    return JsonResponse({"ok": True}, status=200)

server.bind_handlers({
    ("POST", "/create/user"): handler_create_user,
    ("GET", "/"): handler_home_page
})

server.mount("./static")
server.run()
