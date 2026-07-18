export async function getWeather(city) {

    var url = 
        "https://api.open-meteo.com/v1/forecast" +
        "?latitude=" + city.latitude +
        "&longitude=" + city.longitude +
        "&current=temperature_2m,relative_humidity_2m"

    var response = await fetch(url);
    var data = await response.json();

    return data;
    
}