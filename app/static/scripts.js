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
    }).then(response => {});
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
