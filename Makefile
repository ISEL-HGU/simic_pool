DIR := ${CURDIR}

build:
	cd poolprocess;gradle build
	unzip $(CURDIR)/poolprocess/app/build/distributions/app.zip -d PP


unzip:
	rm -rf runs
	unzip $(CURDIR)/app/build/distributions/app.zip

pp_run:
	./PP/app/bin/app -proj $(proj) -pc $(pc) -file $(file) -line $(line)

clean:
	rm -rf PP