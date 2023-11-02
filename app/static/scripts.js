// Get the modal
var modal = document.getElementById('id01');
// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

async function registerUser() {
    const wrongCredentialsSpan = document.getElementById("reg_wrong_credentials");
    const url = "http://localhost:8000/auth/register";
    const username = document.getElementById("reg_uname").value;
    const password = document.getElementById("reg_psw").value;

    await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({username: username, password: password}),
    }).then(response => {
        if (response.status === 200) {
            window.location.href = "/"
        } else {
            wrongCredentialsSpan.textContent = "Что-то пошло не так, попробуйте еще раз";
        }
    });
}

async function loginUser() {
    const wrongCredentialsSpan = document.getElementById("wrong_credentials");
    wrongCredentialsSpan.textContent = "";

    const url = "http://localhost:8000/auth/login";
    const username = document.getElementById("login_uname").value;
    const password = document.getElementById("login_psw").value;

    await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({username: username, password: password}),
    }).then(response => {
        if (response.status === 200) {
            window.location.href = "/rr"
        } else if (response.status === 409){
            wrongCredentialsSpan.textContent = "Логин не активирован - обратитесь к администратору";
        } else {
            wrongCredentialsSpan.textContent = "Неверный логин или пароль";
        }
    });
}

async function rrDownload(query_id, query_name) {
    const url = "http://localhost:8000/rr/download";
    const queryParams = "query_id=" + query_id + "&query_name=" + query_name;

    await fetch(url.concat('?', queryParams), {
        method: 'GET'
    })
    .then(res => {
        const disposition = res.headers.get('Content-Disposition');
        filename = disposition.split(/;(.+)/)[1].split(/=(.+)/)[1];
        if (filename.toLowerCase().startsWith("utf-8''"))
            filename = decodeURIComponent(filename.replace("utf-8''", ''));
        else
            filename = filename.replace(/['"]/g, '');
        return res.blob();
    })
    .then(blob => {
        var url = window.URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
    });
}

async function rrReorder(query_id) {
    const url = "http://localhost:8000/rr/reorder";
    var realy = window.confirm("Вы уверены, что хотите перезаказать все неготовые кадастровые номера?");
    if (realy) {
        await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({query_id: query_id}),
        }).then(response => {});
    } else {
    }
}

async function rrQuery() {
    const url = "http://localhost:8000/rr/query";
    const project = document.getElementById("prj_name").value;
    const q_simple = document.getElementById("query_s").value;
    const q_history = document.getElementById("query_h").value;

    await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({project: project, query_s: q_simple, query_h: q_history}),
    }).then(response => {
        if (response.status === 200) {
            window.location.href = "/rr"
        } else {}
    });
}

async function rrRefresh(query_id) {
    const url = "http://localhost:8000/rr/refresh";
    await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({query_id: query_id}),
    }).then(response => {});
}

async function rrSearch() {
    const query = document.getElementById("rrSearchQuery").value;
    const url = "http://localhost:8000/rr/find"
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({query: query}),
    });
    text = await response.text();
    txtarea = document.getElementById("rr_search_res");
    const linecount = (text.replaceAll('\n', '').length - text.length) / 2
    txtarea.innerText = text.replaceAll(/"/g, "").replaceAll('\n', '\\u000A');
    txtarea.style.height = (100 + (50 * linecount)).toString() + "px";
    const hiddenDiv = document.getElementById("rr_search_area");
    hiddenDiv.style.display = 'inline-block';
}
