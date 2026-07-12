// ============================================================
// Script 00 - Reconstruir y validar el estado de la práctica.
// Objetivo: cargar el snapshot relacional y el modelo documental.
// Prerrequisito: MongoDB saludable y data/ montado en /data/practica.
// Qué observar: 8 colecciones origen y 2 colecciones documentales.
// Advertencia: elimina y recrea solo MONGO_DATABASE.
// ============================================================

const fs = require("fs");
const databaseName = process.env.MONGO_DATABASE || "bdia_clase4";
const practica = db.getSiblingDB(databaseName);
const relationalPath = "/data/practica/origen_relacional";
const documentPath = "/data/practica/modelo_documental";

function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;

  for (let index = 0; index < text.length; index += 1) {
    const character = text[index];
    if (quoted && character === '"' && text[index + 1] === '"') {
      field += '"';
      index += 1;
    } else if (character === '"') {
      quoted = !quoted;
    } else if (character === "," && !quoted) {
      row.push(field);
      field = "";
    } else if ((character === "\n" || character === "\r") && !quoted) {
      if (character === "\r" && text[index + 1] === "\n") index += 1;
      row.push(field);
      if (row.some((value) => value !== "")) rows.push(row);
      row = [];
      field = "";
    } else {
      field += character;
    }
  }
  if (field !== "" || row.length > 0) {
    row.push(field);
    rows.push(row);
  }

  const [headers, ...values] = rows;
  return values.map((cells) => Object.fromEntries(headers.map((header, index) => [header, cells[index]])));
}

function readCsv(fileName) {
  return parseCsv(fs.readFileSync(`${relationalPath}/${fileName}.csv`, "utf8"));
}

function toInteger(document, fields) {
  fields.forEach((field) => { document[field] = NumberInt(document[field]); });
  return document;
}

function toDate(document, fields) {
  fields.forEach((field) => { document[field] = new Date(document[field]); });
  return document;
}

practica.dropDatabase();

const loaders = {
  usuarios: (row) => toDate(toInteger({...row, activo: row.activo === "true"}, ["id"]), ["fecha_alta"]),
  tipos_fuente: (row) => toInteger(row, ["id"]),
  datasets: (row) => toDate(toInteger(row, ["id", "usuario_id", "tipo_fuente_id", "cantidad_registros"]), ["fecha_creacion"]),
  tipos_modelo: (row) => toInteger(row, ["id"]),
  modelos: (row) => toDate(toInteger(row, ["id", "usuario_id", "tipo_modelo_id"]), ["fecha_creacion"]),
  experimentos: (row) => toDate(toInteger({...row, finalizado: row.finalizado === "true"}, ["id", "dataset_id"]), ["fecha"]),
  experimentos_modelos: (row) => ({...toInteger(row, ["experimento_id", "modelo_id"]), parametros_jsonb: JSON.parse(row.parametros_jsonb)}),
  metricas: (row) => toDate({...toInteger(row, ["id", "experimento_id"]), valor: Number(row.valor)}, ["fecha_registro"]),
};

Object.entries(loaders).forEach(([name, transform]) => {
  const documents = readCsv(name).map(transform);
  practica.getCollection(`origen_${name}`).insertMany(documents);
});

const modelos = JSON.parse(fs.readFileSync(`${documentPath}/modelos.json`, "utf8"));
const experimentos = JSON.parse(fs.readFileSync(`${documentPath}/experimentos.json`, "utf8"))
  .map((document) => ({...document, fecha: new Date(`${document.fecha}T00:00:00Z`)}));
practica.modelos.insertMany(modelos);
practica.experimentos.insertMany(experimentos);

const expectedCounts = {
  origen_usuarios: 7,
  origen_tipos_fuente: 6,
  origen_datasets: 9,
  origen_tipos_modelo: 4,
  origen_modelos: 9,
  origen_experimentos: 9,
  origen_experimentos_modelos: 10,
  origen_metricas: 30,
  modelos: 9,
  experimentos: 9,
};

Object.entries(expectedCounts).forEach(([collection, expected]) => {
  const actual = practica.getCollection(collection).countDocuments();
  if (actual !== expected) throw new Error(`${collection}: se esperaban ${expected} documentos y se cargaron ${actual}`);
  print(`${collection.padEnd(31)} ${actual}`);
});

const missingModels = practica.experimentos.aggregate([
  {$unwind: "$ejecuciones"},
  {$lookup: {from: "modelos", localField: "ejecuciones.modelo_id", foreignField: "_id", as: "modelo"}},
  {$match: {modelo: {$size: 0}}},
  {$count: "cantidad"},
]).toArray();
if (missingModels.length > 0) throw new Error("Hay ejecuciones con referencias a modelos inexistentes");

print(`\nCarga completa y consistente en la base ${databaseName}.`);
