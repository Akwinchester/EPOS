// Находим элементы на странице
const form = document.querySelector('#form');
const taskInput = document.querySelector('#taskInput');
const taskInputDate = document.querySelector('#taskInputDate');
const tasksList = document.querySelector('#tasksList');
const emptyList = document.querySelector('#emptyList');
const option = {
	weekday: 'short',
	month: 'short',
	day: 'numeric',
}

let tasks = [];

if (as) {
	tasks = JSON.parse(as);
	tasks.forEach((task) => renderTask(task));
}

checkEmptyList();

form.addEventListener('submit', addTask);
tasksList.addEventListener('click', deleteTask);
tasksList.addEventListener('click', doneTask);

// Функции
function addTask(event) {
	// Отменяем отправку формы
	event.preventDefault();

	// Достаем текст задачи из поля ввода
	const taskText = taskInput.value;

	// Описываем задачу в виде объекта
	const newTask = {
		id: Date.now(),
		text: taskText,
		done: false,
		date: taskInputDate.value,
		status_date: 'true',
	};
	sendRequest('POST', requestURL, newTask)

	// Добавляем задачу в массив с задачами
	tasks.push(newTask);

	// Сохраняем список задач в хранилище браузера localStorage
	saveToLocalStorage();

	// Рендерим задачу на странице
	renderTask(newTask);

	// Очищаем поле ввода и возвращаем на него фокус
	taskInput.value = '';
	taskInput.focus();

	checkEmptyList();
}

function deleteTask(event) {
	// Проверяем если клик был НЕ по кнопке "удалить задачу"
	if (event.target.dataset.action !== 'delete') return;

	const parenNode = event.target.closest('.list-group-item');

	// Определяем ID задачи
	const id = Number(parenNode.id);
	const requestURLdelete = 'http://127.0.0.1:8000/app_reminders/delete/';

	// const tasksid = {id:id};
	sendRequest('POST', requestURLdelete, id);
	// Удаляем задча через фильтрацию массива
	tasks = tasks.filter((task) => task.id !== id);

	// Сохраняем список задач в хранилище браузера localStorage
	saveToLocalStorage();

	// Удаляем задачу из разметки
	parenNode.remove();

	checkEmptyList();
}

function doneTask(event) {
	// Проверяем что клик был НЕ по кнопке "задача выполнена"
	if (event.target.dataset.action !== 'done') return;

	const parentNode = event.target.closest('.list-group-item');

	// Определяем ID задачи
	const id = Number(parentNode.id);
	const task = tasks.find((task) => task.id === id);
	const requestURLstatus = 'http://127.0.0.1:8000/app_reminders/status/';

	task.done = !task.done;
	const taskstatus = {
		id: task.id,
		status: task.done,
		}
	sendRequest('POST', requestURLstatus, taskstatus)

	// Сохраняем список задач в хранилище браузера localStorage
	saveToLocalStorage();

	const taskTitle = parentNode.querySelector('.task-title');
	taskTitle.classList.toggle('task-title--done');
}

function checkEmptyList() {
	if (tasks.length === 0) {
		const emptyListHTML = `<li id="emptyList" class="list-group-item empty-list">
					<img src="/static/app_reminders/images/leaf.svg" alt="Empty" width="48" class="mt-3">
					<div class="empty-list__title">Список дел пуст</div>
				</li>`;
		tasksList.insertAdjacentHTML('afterbegin', emptyListHTML);
	}

	if (tasks.length > 0) {
		const emptyListEl = document.querySelector('#emptyList');
		emptyListEl ? emptyListEl.remove() : null;
	}
}

function saveToLocalStorage() {
	localStorage.setItem('tasks', JSON.stringify(tasks))
}

function renderTask(task) {
	// Формируем CSS класс
	const cssClass = task.done ? 'task-title task-title--done' : 'task-title';
	const cssColorClass = (task.status_date === 'true') ? 'status-true': 'status-false'


	
	//Обрабатываем дату в новый формат
	let taskDate = new Date(task.date);
	if (!task.date){
		taskDate = '';
	}
	taskDate = taskDate.toLocaleString('ru-RU', option);


	
	// Формируем разметку для новой задачи
	const taskHTML = `
                <li id="${task.id}" class="list-group-item d-flex justify-content-between task-item">
					<span class="${cssClass} linebreak">${task.text}</span>
					<div class="task-item__buttons">
						<button type="button" data-action="done" class="btn-action">
							<img src="/static/app_reminders/images/tick.svg" alt="Done" width="18" height="18">
						</button>
						<button type="button" data-action="delete" class="btn-action">
							<img src="/static/app_reminders/images/cross.svg" alt="Done" width="18" height="18">
						</button>
					</div>
					<div class="break"></div>
					<div class="${cssColorClass}">${taskDate}</div>
				</li>`;

	// Добавляем задачу на страницу
	tasksList.insertAdjacentHTML('beforeend', taskHTML);
}
