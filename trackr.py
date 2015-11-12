import core

if __name__ == "__main__":
	core.reset_db()
	core.app.run(host='0.0.0.0', port=8080, debug=True)