SELECT *
FROM 
PortfolioProject.dbo.CovidDeaths
ORDER BY 1,2

SELECT *
FROM 
PortfolioProject.dbo.CovidVaccinations
ORDER BY 3,4


SELECT Location, date, total_cases, new_cases, total_deaths, population
FROM 
PortfolioProject.dbo.CovidDeaths
ORDER BY 1,2

-- Looking at total cases vs total deaths
-- shows likelihood of dying if you get infected

SELECT Location, date, total_cases, total_deaths, (total_deaths/total_cases)*100 as DeathPercentage
FROM 
PortfolioProject.dbo.CovidDeaths
WHERE location like '%states%'
ORDER BY 1,2


-- Looking at the total cases vs the population
-- Shows what percentage of population got covid

SELECT Location, date, total_cases, Population, (total_cases/Population)*100 as InfectionPercentage
FROM 
PortfolioProject.dbo.CovidDeaths
--WHERE location like '%Bangladesh%'
ORDER BY 1,2

--Looking at countries with highest infection rate

SELECT Location, Population, MAX(total_cases) as HighestInfectionCount, MAX((total_cases/Population))*100 as InfectionPercentage
FROM 
PortfolioProject.dbo.CovidDeaths
--WHERE location like '%Bangladesh%'
Group by Location, Population
ORDER BY InfectionPercentage DESC


-- SHOWING THE COUNTRIES WITH THE HIGHEST DEATH COUNT PER POP

SELECT Location, MAX(cast(total_deaths as int))  as TotalDeathCount
FROM 
PortfolioProject.dbo.CovidDeaths
WHERE continent is not null
Group by Location
ORDER BY TotalDeathCount DESC

-- Looking at data by continent

SELECT location, MAX(cast(Total_deaths as int))  as TotalDeathCount
FROM 
PortfolioProject.dbo.CovidDeaths
WHERE continent is null
Group by location
ORDER BY TotalDeathCount DESC

-- Showing the continents with the highest death counts

SELECT continent, MAX(cast(Total_deaths as int))  as TotalDeathCount
FROM 
PortfolioProject.dbo.CovidDeaths
WHERE continent is not null
Group by continent
ORDER BY TotalDeathCount DESC

-- Global numbers 

SELECT SUM(new_cases) as TotalCases, SUM(cast(new_deaths as int)) as TotalDeaths,
SUM(cast(new_deaths as int))/SUM(new_cases)*100 as DeathPercentage
FROM 
PortfolioProject.dbo.CovidDeaths
--WHERE location like '%states%'
WHERE continent is not null
--Group by date
ORDER BY 1,2

-- Looking at Total Population vs Vaccinations

SELECT CD.continent, CD.location, CD.date, CD.population, VAC.new_vaccinations,
SUM(cast(VAC.new_vaccinations as int)) OVER (Partition by CD.location ORDER BY CD.location,
CD.date) as RollingPeopleVaccinated
FROM 
PortfolioProject.dbo.CovidDeaths CD
 JOIN PortfolioProject..CovidVaccinations VAC
 ON CD.location = VAC.location
 AND CD.date = VAC.date
 WHERE CD.continent is not null
 ORDER BY 2,3

 --USE CTE

 With PopVsVac (continent, location, date, population, new_vaccinations, RollingPeopleVaccinated)
 as
 (
SELECT CD.continent, CD.location, CD.date, CD.population, VAC.new_vaccinations,
SUM(cast(VAC.new_vaccinations as int)) OVER (Partition by CD.location ORDER BY CD.location,
CD.date) as RollingPeopleVaccinated
FROM 
PortfolioProject.dbo.CovidDeaths CD
 JOIN PortfolioProject..CovidVaccinations VAC
 ON CD.location = VAC.location
 AND CD.date = VAC.date
 WHERE CD.continent is not null
 --ORDER BY 2,3
)


Select *,(RollingPeopleVaccinated/population)*100
FROM
PopVsVac


--Temp Table


DROP Table if exists #PercentagePeopleVaccinated
Create Table #PercentagePeopleVaccinated
(
Continent nvarchar(255),
Location nvarchar(255),
Date datetime,
Population numeric, 
New_vaccinations numeric,
RollingPeopleVaccinated numeric
)
Insert into #PercentagePeopleVaccinated
SELECT CD.continent, CD.location, CD.date, CD.population, VAC.new_vaccinations,
SUM(cast(VAC.new_vaccinations as int)) OVER (Partition by CD.location ORDER BY CD.location,
CD.date) as RollingPeopleVaccinated
FROM 
PortfolioProject.dbo.CovidDeaths CD
 JOIN PortfolioProject..CovidVaccinations VAC
 ON CD.location = VAC.location
 AND CD.date = VAC.date
 --WHERE CD.continent is not null
 --ORDER BY 2,3

 

SELECT *, (RollingPeopleVaccinated/Population)*100
FROM
#PercentagePeopleVaccinated


--Creating view to store data fro later visualizations
DROP VIEW if exists PercentPopulationVaccinated
Create VIEW PercentPopulationVaccinated as
SELECT CD.continent, CD.location, CD.date, CD.population, VAC.new_vaccinations,
SUM(cast(VAC.new_vaccinations as int)) OVER (Partition by CD.location ORDER BY CD.location,
CD.date) as RollingPeopleVaccinated
FROM 
PortfolioProject.dbo.CovidDeaths CD
 JOIN PortfolioProject..CovidVaccinations VAC
 ON CD.location = VAC.location
 AND CD.date = VAC.date
 WHERE CD.continent is not null
 --ORDER BY 2,3


































